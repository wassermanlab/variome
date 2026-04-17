import csv
import io
import zipfile

from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection, OperationalError, ProgrammingError
from django.http import HttpResponse


# The three legacy pghistory event tables preserved for auditability.
LEGACY_TABLES = [
    "library_access_userprofileevent",
    "library_access_libraryuserevent",
    "library_access_librarygroupevent",
]


@staff_member_required
def pghistory_export(request):
    """Export legacy pghistory event tables as a ZIP archive of CSV files.

    Only accessible to staff members.  Each legacy table is exported as a
    separate CSV file inside the ZIP.  If a table does not exist (e.g. on a
    fresh database that never ran pghistory) a plain-text note is included
    instead.
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for table in LEGACY_TABLES:
            try:
                with connection.cursor() as cursor:
                    # table is sourced from the LEGACY_TABLES constant above;
                    # quote_name provides safe SQL identifier escaping.
                    cursor.execute(
                        "SELECT * FROM %s ORDER BY 1"
                        % connection.ops.quote_name(table)
                    )
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()

                csv_buf = io.StringIO()
                writer = csv.writer(csv_buf)
                writer.writerow(columns)
                writer.writerows(rows)
                zf.writestr(f"{table}.csv", csv_buf.getvalue())

            except (OperationalError, ProgrammingError):
                zf.writestr(
                    f"{table}_not_found.txt",
                    f"Table '{table}' was not found in the database.\n"
                    "This is expected on fresh installations that never ran pghistory.\n",
                )

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.read(), content_type="application/zip")
    response["Content-Disposition"] = (
        'attachment; filename="pghistory_legacy_export.zip"'
    )
    return response
