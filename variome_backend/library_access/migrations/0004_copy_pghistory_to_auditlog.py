"""
Reversible data migration that copies historical records from the three legacy
django-pghistory event tables into django-auditlog's LogEntry table.

Legacy source tables (preserved by migration 0003):
  library_access_userprofileevent   → UserProfile history
  library_access_libraryuserevent   → User (LibraryUser) history
  library_access_librarygroupevent  → Group (LibraryGroup) history

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


def _extract_user_id_from_metadata(metadata):
    """
    Try to extract an integer user ID from a pgh_context metadata value.

    Different pghistory configurations store the actor under different keys.
    The most common default is ``{"user": <pk>}`` (set by
    ``pghistory.middleware.HistoryMiddleware``), but projects sometimes use
    ``"user_id"`` or ``"user_pk"`` instead.

    Returns the integer user pk, or None if none of the known keys are present
    or the stored value cannot be coerced to an integer.
    """
    if metadata is None:
        return None
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except (ValueError, TypeError):
            return None
    if not isinstance(metadata, dict):
        return None
    for key in ("user", "user_id", "user_pk"):
        value = metadata.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _load_actor_map(connection):
    """
    Return a mapping  {str(pgh_context_id): user_id}  sourced from the
    pgh_context table, filtered to user IDs that still exist in auth_user.

    Returns an empty dict if the pgh_context table is absent.

    Two pgh_context schema variants are handled:

    * **metadata column** (pghistory default) – the actor is stored as JSON
      inside a ``metadata`` JSONB column, keyed by ``"user"``, ``"user_id"``,
      or ``"user_pk"``.
    * **direct user_id column** – some projects create a custom context model
      with an explicit ``user_id`` integer FK; this column is read directly.
    """
    with connection.cursor() as cur:
        # --- Check whether pgh_context exists at all ---
        cur.execute(
            "SELECT EXISTS("
            "  SELECT 1 FROM information_schema.tables"
            "  WHERE table_schema = 'public' AND table_name = 'pgh_context'"
            ")"
        )
        if not cur.fetchone()[0]:
            return {}

        # --- Discover pgh_context column names ---
        cur.execute("SELECT * FROM pgh_context WHERE 1=0")
        ctx_columns = {desc[0] for desc in cur.description}

        # --- Collect valid user IDs still present in auth_user ---
        cur.execute("SELECT id FROM auth_user")
        valid_user_ids = {row[0] for row in cur.fetchall()}

        actor_map = {}

        # Variant A: direct user_id column on pgh_context
        if "user_id" in ctx_columns:
            cur.execute(
                "SELECT id, user_id FROM pgh_context WHERE user_id IS NOT NULL"
            )
            for ctx_id, user_id in cur.fetchall():
                try:
                    user_id = int(user_id)
                except (TypeError, ValueError):
                    continue
                if user_id in valid_user_ids and ctx_id is not None:
                    actor_map[str(ctx_id)] = user_id
            return actor_map

        # Variant B: metadata JSONB column
        if "metadata" in ctx_columns:
            cur.execute(
                "SELECT id, metadata FROM pgh_context WHERE metadata IS NOT NULL"
            )
            for ctx_id, metadata in cur.fetchall():
                user_id = _extract_user_id_from_metadata(metadata)
                if user_id is not None and user_id in valid_user_ids and ctx_id is not None:
                    actor_map[str(ctx_id)] = user_id
            return actor_map

        # pgh_context exists but has neither expected column — return empty
        return actor_map


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
