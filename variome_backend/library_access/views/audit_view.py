import json
import logging
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection, OperationalError, ProgrammingError
from django.shortcuts import render

log = logging.getLogger(__file__)


class _AuditEncoder(json.JSONEncoder):
    """JSON encoder that handles types commonly returned by database cursors."""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


# Legacy pghistory event tables preserved for auditability.
LEGACY_TABLES = [
    "library_access_userprofileevent",
    "library_access_libraryuserevent",
    "library_access_librarygroupevent",
]

# Human-readable label for each table shown in the Audit View.
TABLE_LABELS = {
    "library_access_userprofileevent": "User Profile Events",
    "library_access_libraryuserevent": "User Events",
    "library_access_librarygroupevent": "Group Events",
}


def _read_table(table):
    """Return (columns, rows) for a legacy pghistory event table.

    Returns (None, None) if the table does not exist.
    """
    try:
        with connection.cursor() as cursor:
            # First fetch column names so we can order by a specific column.
            cursor.execute(
                "SELECT * FROM %s WHERE 1=0"
                % connection.ops.quote_name(table)
            )
            columns = [desc[0] for desc in cursor.description]

        # Order by the first column that looks like a primary-key / event id,
        # falling back to the very first column.
        order_col = next(
            (c for c in columns if c in ("pgh_id", "id", "history_id")),
            columns[0] if columns else None,
        )
        if not order_col:
            return [], []
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM %s ORDER BY %s DESC"
                % (
                    connection.ops.quote_name(table),
                    connection.ops.quote_name(order_col),
                )
            )
            rows = cursor.fetchall()
        return columns, rows
    except (OperationalError, ProgrammingError):
        return None, None


@staff_member_required
def audit_view(request):
    """Render the Audit View page showing legacy pghistory event data.

    Only accessible to staff members.
    """
    tables = []
    for table in LEGACY_TABLES:
        columns, rows = _read_table(table)
        if columns is not None:
            tables.append(
                {
                    "name": table,
                    "label": TABLE_LABELS.get(table, table),
                    "columns": columns,
                    "rows": [list(row) for row in rows],
                    "count": len(rows),
                }
            )
        else:
            tables.append(
                {
                    "name": table,
                    "label": TABLE_LABELS.get(table, table),
                    "columns": [],
                    "rows": [],
                    "count": 0,
                    "missing": True,
                }
            )

    context = {
        "data": json.dumps({"tables": tables}, cls=_AuditEncoder),
    }
    return render(request, "audit_view.html", context)
