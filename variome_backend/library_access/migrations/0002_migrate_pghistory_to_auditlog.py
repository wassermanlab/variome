"""
Combined migration that copies all historical records from the three legacy
django-pghistory event tables into django-auditlog's LogEntry table.

All reads use Django ORM queries (apps.get_model + .values()) rather than
raw SQL, so:
  * No direct pghistory/pgtrigger imports are needed inside the functions.
  * When pghistory is later removed from the project and its models disappear
    from the migration registry, every apps.get_model() call raises LookupError
    which is caught and treated as "nothing to migrate" — the migration still
    runs cleanly on a fresh database.

Legacy source models (library_access app):
  UserProfileEvent  → UserProfile history
  LibraryUserEvent  → User (LibraryUser) history
  LibraryGroupEvent → Group (LibraryGroup) history

Actor resolution: the pghistory Context model (app label "pghistory") stores
a metadata JSONB column whose "user" key holds the acting user's PK as a
string.  We build a Python dict {context_id: user_pk} once and reuse it for
all event rows — equivalent to the previous SQL JOIN but without raw SQL.

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

# attname values that belong to pghistory bookkeeping, not the model snapshot.
_PGH_META_ATTNAMES = {
    "pgh_id",
    "pgh_created_at",
    "pgh_label",
    "pgh_context_id",
    "pgh_obj_id",
}

# Fields whose values are omitted from the changes dict (sensitive or useless).
_SKIP_ATTNAMES = {"password"}


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


def _build_context_user_map(apps):
    """
    Return a {context_id: user_pk} mapping built from the pghistory Context
    model.  Returns an empty dict if the model is not in the migration registry
    (i.e. pghistory has been removed from the project).
    """
    try:
        Context = apps.get_model("pghistory", "Context")
    except LookupError:
        return {}

    user_map = {}
    for ctx in Context.objects.values("id", "metadata"):
        metadata = ctx.get("metadata") or {}
        user_str = metadata.get("user")
        if user_str:
            try:
                user_map[ctx["id"]] = int(user_str)
            except (ValueError, TypeError):
                pass
    return user_map


def _snapshot_attnames(EventModel):
    """
    Return the list of field attnames that represent a model snapshot (i.e.
    everything except pghistory bookkeeping columns and skipped fields).

    Uses concrete_fields so that ForeignKey attnames include the trailing _id
    (e.g. 'pgh_context_id') which matches what .values() returns.
    """
    return [
        f.attname
        for f in EventModel._meta.concrete_fields
        if f.attname not in _PGH_META_ATTNAMES and f.attname not in _SKIP_ATTNAMES
    ]


def _migrate_event_model(apps, event_model_name,
                         content_type, LogEntry, context_user_map):
    """
    Read *event_model_name* via the ORM and bulk-insert LogEntry rows.
    Skips gracefully if the model is not in the migration registry.
    """
    try:

        from variome_backend.library_access import models
        modelMap = {
            "LibraryUserEvent": models.LibraryUserEvent,
            "LibraryGroupEvent": models.LibraryGroupEvent,
            "UserProfileEvent": models.UserProfileEvent,
        }
        EventModel = modelMap.get(event_model_name)
    except LookupError:
        return  # pghistory removed — nothing to migrate


    snapshot_attnames = _snapshot_attnames(EventModel)
    if not snapshot_attnames:
        return

    rows = EventModel.objects.order_by("pgh_id").values(
        "pgh_id",
        "pgh_created_at",
        "pgh_label",
        "pgh_obj_id",
        "pgh_context_id",
        *snapshot_attnames,
    )

    if not rows.exists():
        return

    last_snapshot = {}  # {pgh_obj_id: {field: value}}
    entries = []

    for row in rows:
        pgh_id = row["pgh_id"]
        pgh_created_at = row["pgh_created_at"]
        pgh_label = row["pgh_label"]
        obj_id = row["pgh_obj_id"]
        context_id = row["pgh_context_id"]

        actor_id = context_user_map.get(context_id)

        snapshot = {k: row[k] for k in snapshot_attnames}

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
    if schema_editor.connection.vendor != "postgresql":
        return

    from auditlog.models import LogEntry
    from django.contrib.contenttypes.models import ContentType

    context_user_map = _build_context_user_map(apps)

    # (event model name in library_access, content-type app_label, model_name)
    model_map = [
        ("LibraryUserEvent", "auth", "user"),
        ("LibraryGroupEvent", "auth", "group"),
        ("UserProfileEvent", "library_access", "userprofile"),
    ]

    for event_model_name, ct_app_label, ct_model_name in model_map:
        try:
            ct = ContentType.objects.get(app_label=ct_app_label, model=ct_model_name)
        except ContentType.DoesNotExist:
            continue
        _migrate_event_model(
            apps, event_model_name, ct, LogEntry, context_user_map
        )


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
