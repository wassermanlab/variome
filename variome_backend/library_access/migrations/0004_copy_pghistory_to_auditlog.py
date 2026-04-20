"""
Reversible data migration that copies historical records from the three legacy
django-pghistory event tables into django-auditlog's LogEntry table.

Legacy source tables (preserved by migration 0003):
  library_access_userprofileevent   → UserProfile history
  library_access_libraryuserevent   → User (LibraryUser) history
  library_access_librarygroupeent   → Group (LibraryGroup) history

Each source row maps to one LogEntry:
  pgh_label = 'insert'  → Action.CREATE  (all fields shown as None → value)
  pgh_label = 'update'  → Action.UPDATE  (only changed fields, diffed against
                                           the preceding snapshot for that object)
  any other label       → Action.UPDATE

The actor is resolved from the pgh_context table when it is present.

Every migrated entry is tagged with
  additional_data = {"migrated_from_pghistory": True, ...}
so the reverse operation can cleanly delete exactly those rows.
"""

import json

from django.db import migrations


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Columns that belong to pghistory's own bookkeeping, not the model snapshot.
_PGH_META = {"pgh_id", "pgh_created_at", "pgh_label", "pgh_context_id", "pgh_obj_id"}

# Fields whose values are omitted from the changes dict (sensitive or useless).
_SKIP_FIELDS = {"password"}


def _to_str(v):
    """Return None unchanged; convert everything else to str."""
    return None if v is None else str(v)


def _create_changes(snapshot):
    """Build an auditlog changes dict for a CREATE event (None → value)."""
    return {k: [None, _to_str(v)] for k, v in snapshot.items()}


def _update_changes(prev, curr):
    """Build an auditlog changes dict containing only the fields that changed."""
    return {
        k: [_to_str(prev.get(k)), _to_str(v)]
        for k, v in curr.items()
        if prev.get(k) != v
    }


def _load_actor_map(connection):
    """
    Return a mapping  {str(pgh_context_id): user_id}  sourced from the
    pgh_context table, filtered to user IDs that still exist in auth_user.

    Returns an empty dict if the pgh_context table is absent or inaccessible.
    """
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT EXISTS("
                "  SELECT 1 FROM information_schema.tables"
                "  WHERE table_schema = 'public' AND table_name = 'pgh_context'"
                ")"
            )
            if not cur.fetchone()[0]:
                return {}

            cur.execute("SELECT id FROM auth_user")
            valid_user_ids = {row[0] for row in cur.fetchall()}

            cur.execute("SELECT id, metadata FROM pgh_context")
            actor_map = {}
            for ctx_id, metadata in cur.fetchall():
                if metadata is None:
                    continue
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except (ValueError, TypeError):
                        continue
                user_id = metadata.get("user")
                try:
                    user_id = int(user_id)
                except (TypeError, ValueError):
                    continue
                if user_id in valid_user_ids and ctx_id is not None:
                    actor_map[str(ctx_id)] = user_id
            return actor_map
    except Exception:
        return {}


def _migrate_table(connection, table_name, content_type, LogEntry, actor_map):
    """
    Read *table_name* and bulk-insert the corresponding LogEntry rows.

    Does nothing if the table does not exist.
    """
    with connection.cursor() as cur:
        cur.execute(
            "SELECT EXISTS("
            "  SELECT 1 FROM information_schema.tables"
            "  WHERE table_schema = 'public' AND table_name = %s"
            ")",
            [table_name],
        )
        if not cur.fetchone()[0]:
            return  # fresh installation — table was never created

        # Discover columns present in this particular event table.
        cur.execute(
            "SELECT * FROM %s WHERE 1=0" % connection.ops.quote_name(table_name)
        )
        all_columns = [desc[0] for desc in cur.description]

        # Columns that represent a model-field snapshot.
        snapshot_cols = [
            c for c in all_columns if c not in _PGH_META and c not in _SKIP_FIELDS
        ]

        if not snapshot_cols:
            return

        col_idx = {col: i for i, col in enumerate(all_columns)}

        cur.execute(
            "SELECT * FROM %s ORDER BY pgh_id"
            % connection.ops.quote_name(table_name)
        )
        raw_rows = cur.fetchall()

    if not raw_rows:
        return

    # One snapshot dict per tracked-object id so we can diff UPDATE events.
    last_snapshot = {}  # {pgh_obj_id: {field: value}}
    entries = []

    for row in raw_rows:
        pgh_id = row[col_idx["pgh_id"]]
        pgh_created_at = row[col_idx["pgh_created_at"]]
        pgh_label = row[col_idx["pgh_label"]]
        pgh_context_id = row[col_idx["pgh_context_id"]]
        obj_id = row[col_idx["pgh_obj_id"]]

        snapshot = {c: row[col_idx[c]] for c in snapshot_cols}

        if pgh_label == "insert":
            action = LogEntry.Action.CREATE
        else:
            action = LogEntry.Action.UPDATE

        if action == LogEntry.Action.CREATE or obj_id not in last_snapshot:
            changes = _create_changes(snapshot)
        else:
            changes = _update_changes(last_snapshot[obj_id], snapshot)

        last_snapshot[obj_id] = snapshot

        actor_id = (
            actor_map.get(str(pgh_context_id)) if pgh_context_id is not None else None
        )

        # Best-effort human-readable representation using snapshot fields.
        obj_repr = (
            snapshot.get("username")
            or snapshot.get("name")
            or str(obj_id)
        )

        entries.append(
            LogEntry(
                content_type_id=content_type.pk,
                object_pk=str(obj_id),
                object_id=int(obj_id),
                object_repr=obj_repr,
                action=action,
                changes=changes,
                changes_text="",
                actor_id=actor_id,
                remote_addr=None,
                timestamp=pgh_created_at,
                additional_data={
                    "migrated_from_pghistory": True,
                    "pgh_id": pgh_id,
                    "pgh_label": pgh_label,
                },
            )
        )

    LogEntry.objects.bulk_create(entries, batch_size=500)


# ---------------------------------------------------------------------------
# Forward migration
# ---------------------------------------------------------------------------

def copy_pghistory_to_auditlog(apps, schema_editor):
    from auditlog.models import LogEntry
    from django.contrib.contenttypes.models import ContentType

    if schema_editor.connection.vendor != "postgresql":
        return

    actor_map = _load_actor_map(schema_editor.connection)

    # (legacy table, app_label, model) — model_name must match Django's
    # ContentType.model (lower-case).
    table_map = [
        ("library_access_libraryuserevent", "auth", "user"),
        ("library_access_librarygroupevent", "auth", "group"),
        ("library_access_userprofileevent", "library_access", "userprofile"),
    ]

    for table_name, app_label, model_name in table_map:
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            continue  # content type not registered yet; skip
        _migrate_table(
            schema_editor.connection, table_name, ct, LogEntry, actor_map
        )


# ---------------------------------------------------------------------------
# Reverse migration
# ---------------------------------------------------------------------------

def remove_migrated_entries(apps, schema_editor):
    from auditlog.models import LogEntry

    # Delete only the entries that this migration imported.
    LogEntry.objects.filter(
        additional_data__has_key="migrated_from_pghistory"
    ).delete()


# ---------------------------------------------------------------------------
# Migration class
# ---------------------------------------------------------------------------

class Migration(migrations.Migration):

    dependencies = [
        ("library_access", "0003_remove_pghistory_tables"),
    ]

    operations = [
        migrations.RunPython(
            copy_pghistory_to_auditlog,
            reverse_code=remove_migrated_entries,
        ),
    ]
