"""
Combined migration that copies all historical records from the three legacy
django-pghistory event tables into django-auditlog's LogEntry table.  The
actor (user) is resolved by JOINing pgh_context on pgh_context_id and
reading pgh_context.metadata->>'user', letting PostgreSQL handle the UUID
comparison natively.

Legacy source tables:
  library_access_userprofileevent   → UserProfile history
  library_access_libraryuserevent   → User (LibraryUser) history
  library_access_librarygroupevent  → Group (LibraryGroup) history

Each source row maps to one LogEntry:
  pgh_label = 'insert'  → Action.CREATE  (all fields shown as None → value)
  pgh_label = 'update'  → Action.UPDATE  (only changed fields, diffed against
                                           the preceding snapshot for that object)
  any other label       → Action.UPDATE

Every migrated entry is tagged with
  additional_data = {"migrated_from_pghistory": True, ...}
so the reverse operation can cleanly delete exactly those rows.
"""

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


def _pgh_context_exists(connection):
    """Return True if the pgh_context table is present in the public schema."""
    with connection.cursor() as cur:
        cur.execute(
            "SELECT EXISTS("
            "  SELECT 1 FROM information_schema.tables"
            "  WHERE table_schema = 'public' AND table_name = 'pgh_context'"
            ")"
        )
        return cur.fetchone()[0]


def _migrate_table(connection, table_name, content_type, LogEntry, has_pgh_context):
    """
    Read *table_name* and bulk-insert the corresponding LogEntry rows.

    The actor is resolved at the SQL level by JOINing pgh_context (when it
    exists) and then auth_user, so PostgreSQL performs the UUID comparison
    natively and avoids any Python-level type-mismatch.

    Does nothing if the table does not exist.
    """
    tbl = connection.ops.quote_name(table_name)

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
        cur.execute("SELECT * FROM %s WHERE 1=0" % tbl)
        all_columns = [desc[0] for desc in cur.description]

        # Columns that represent a model-field snapshot.
        snapshot_cols = [
            c for c in all_columns if c not in _PGH_META and c not in _SKIP_FIELDS
        ]

        if not snapshot_cols:
            return

        # The actor column is appended at the end of every row.
        col_idx = {col: i for i, col in enumerate(all_columns + ["_actor_id"])}

        if has_pgh_context:
            # Resolve actor via a SQL JOIN so PostgreSQL handles UUID equality.
            # auth_user.id is cast to text to match the JSONB text extraction.
            sql = (
                "SELECT {tbl}.*, __u.id AS _actor_id"
                " FROM {tbl}"
                " LEFT JOIN pgh_context __ctx ON {tbl}.pgh_context_id = __ctx.id"
                " LEFT JOIN auth_user __u"
                "   ON __u.id::text = __ctx.metadata->>'user'"
                " ORDER BY {tbl}.pgh_id"
            ).format(tbl=tbl)
        else:
            sql = (
                "SELECT {tbl}.*, NULL AS _actor_id"
                " FROM {tbl}"
                " ORDER BY {tbl}.pgh_id"
            ).format(tbl=tbl)

        cur.execute(sql)
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
        obj_id = row[col_idx["pgh_obj_id"]]
        actor_id = row[col_idx["_actor_id"]]

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

def migrate_pghistory_to_auditlog(apps, schema_editor):
    connection = schema_editor.connection

    if connection.vendor != "postgresql":
        return

    from auditlog.models import LogEntry
    from django.contrib.contenttypes.models import ContentType

    has_pgh_context = _pgh_context_exists(connection)

    # (legacy table, app_label, model_name)
    table_map = [
        ("library_access_libraryuserevent", "auth", "user"),
        ("library_access_librarygroupevent", "auth", "group"),
        ("library_access_userprofileevent", "library_access", "userprofile"),
    ]

    for table_name, app_label, model_name in table_map:
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            continue
        _migrate_table(connection, table_name, ct, LogEntry, has_pgh_context)


# ---------------------------------------------------------------------------
# Reverse migration
# ---------------------------------------------------------------------------

def reverse_migrate_pghistory_to_auditlog(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    from auditlog.models import LogEntry

    # Remove only the entries that this migration imported.
    # The legacy tables and triggers cannot be trivially recreated.
    LogEntry.objects.filter(
        additional_data__has_key="migrated_from_pghistory"
    ).delete()


# ---------------------------------------------------------------------------
# Migration class
# ---------------------------------------------------------------------------

class Migration(migrations.Migration):

    dependencies = [
        ("library_access", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            migrate_pghistory_to_auditlog,
            reverse_code=reverse_migrate_pghistory_to_auditlog,
        ),
    ]
