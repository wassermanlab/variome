import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote as urlquote

import psycopg2
import psycopg2.sql
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# Maximum number of numeric suffixes to try when the base name is taken
_MAX_DB_NAME_ATTEMPTS = 100

# Only allow safe identifiers: start with a letter, then letters/digits/underscores
_IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def _validate_identifier(value, label):
    """Raise CommandError if *value* is not a safe PostgreSQL identifier."""
    if not _IDENTIFIER_RE.match(value):
        raise CommandError(
            f"Invalid {label} '{value}'. "
            "Only letters, digits, and underscores are allowed, "
            "and the value must start with a letter."
        )


class Command(BaseCommand):
    help = (
        "Bootstrap a new PostgreSQL database for development. "
        "Creates the database, user, and grants privileges as described in the README."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--host",
            default="localhost",
            help="PostgreSQL server host (default: localhost)",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=5432,
            help="PostgreSQL server port (default: 5432)",
        )
        parser.add_argument(
            "--admin-user",
            default="postgres",
            dest="admin_user",
            help="PostgreSQL superuser name for initial connection (default: postgres)",
        )
        parser.add_argument(
            "--admin-password",
            default="",
            dest="admin_password",
            help="PostgreSQL superuser password (default: empty, uses peer/trust auth)",
        )
        parser.add_argument(
            "--db-name",
            default="variome",
            dest="db_name",
            help="Base name for the new database (default: variome)",
        )
        parser.add_argument(
            "--db-user",
            default="variome",
            dest="db_user",
            help="Database user to create (default: variome)",
        )
        parser.add_argument(
            "--db-password",
            default="variome",
            dest="db_password",
            help="Password for the database user (default: variome)",
        )
        parser.add_argument(
            "--update-env",
            dest="update_env",
            action="store_true",
            default=False,
            help="Automatically update the DB variable in .env without prompting",
        )
        parser.add_argument(
            "--no-input",
            "--noinput",
            dest="no_input",
            action="store_true",
            default=False,
            help="Skip the interactive .env update prompt (do not update .env)",
        )

    def handle(self, **options):
        host = options["host"]
        port = options["port"]
        admin_user = options["admin_user"]
        admin_password = options["admin_password"]
        base_db_name = options["db_name"]
        db_user = options["db_user"]
        db_password = options["db_password"]
        update_env = options["update_env"]
        no_input = options["no_input"]

        _validate_identifier(base_db_name, "db-name")
        _validate_identifier(db_user, "db-user")

        self.stdout.write("Connecting to PostgreSQL server...")
        conn = self._connect_admin(host, port, admin_user, admin_password)
        if conn is None:
            sys.exit(1)

        conn.autocommit = True
        cur = conn.cursor()

        # Find an available database name
        db_name = self._find_available_db_name(cur, base_db_name)

        # Create the database (identifiers cannot be parameterized; validated above)
        self.stdout.write(f"Creating database '{db_name}'...")
        cur.execute(
            psycopg2.sql.SQL("CREATE DATABASE {}").format(
                psycopg2.sql.Identifier(db_name)
            )
        )

        # Create the user if it doesn't exist
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
        if cur.fetchone():
            self.stdout.write(
                f"User '{db_user}' already exists, skipping user creation."
            )
        else:
            self.stdout.write(f"Creating user '{db_user}'...")
            cur.execute(
                psycopg2.sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    psycopg2.sql.Identifier(db_user)
                ),
                (db_password,),
            )

        # Grant privileges
        self.stdout.write(
            f"Granting all privileges on '{db_name}' to '{db_user}'..."
        )
        cur.execute(
            psycopg2.sql.SQL(
                "GRANT ALL PRIVILEGES ON DATABASE {} TO {}"
            ).format(
                psycopg2.sql.Identifier(db_name),
                psycopg2.sql.Identifier(db_user),
            )
        )

        cur.close()
        conn.close()

        db_url = (
            f"postgresql://{urlquote(db_user, safe='')}:"
            f"{urlquote(db_password, safe='')}@{host}:{port}/{db_name}"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDatabase '{db_name}' created successfully!\n"
                f"Connection string: {db_url}"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "Note: the connection string above contains the database password "
                "in plain text. This is normal for a local dev setup."
            )
        )

        self._offer_update_env(db_url, update_env=update_env, no_input=no_input)

    def _connect_admin(self, host, port, admin_user, admin_password):
        """Connect to the PostgreSQL server using the maintenance database."""
        conn_kwargs = {
            "host": host,
            "port": port,
            "user": admin_user,
            "database": "postgres",
        }
        if admin_password:
            conn_kwargs["password"] = admin_password
        try:
            return psycopg2.connect(**conn_kwargs)
        except psycopg2.OperationalError as e:
            self.stderr.write(f"Error connecting to PostgreSQL: {e}")
            self.stderr.write(
                "Tips:\n"
                "  - Ensure PostgreSQL is running.\n"
                "  - On Linux, try: sudo -u postgres python manage.py bootstrap_db\n"
                "  - On Windows/Mac, use --admin-user and --admin-password if needed.\n"
                "  - Use --host/--port to override connection defaults."
            )
            return None

    def _find_available_db_name(self, cur, base_name):
        """Return base_name if available, otherwise try base_name2, base_name3, ...

        Raises CommandError if no available name is found within the attempt limit.
        """
        cur.execute("SELECT datname FROM pg_database")
        existing_dbs = {row[0] for row in cur.fetchall()}

        if base_name not in existing_dbs:
            return base_name

        for i in range(2, _MAX_DB_NAME_ATTEMPTS + 2):
            candidate = f"{base_name}{i}"
            if candidate not in existing_dbs:
                self.stdout.write(
                    f"Database '{base_name}' already exists, "
                    f"using '{candidate}' instead."
                )
                return candidate

        raise CommandError(
            f"Could not find an available database name after {_MAX_DB_NAME_ATTEMPTS} "
            f"attempts (tried '{base_name}' through '{base_name}{_MAX_DB_NAME_ATTEMPTS + 1}'). "
            "Please specify a different base name with --db-name."
        )

    def _offer_update_env(self, db_url, *, update_env=False, no_input=False):
        """Offer to update the DB variable in the .env file."""
        env_path = Path(settings.BASE_DIR) / ".env"

        if not env_path.exists():
            self.stdout.write(
                f"\nNo .env file found at {env_path}.\n"
                f"You can set DB={db_url} manually (copy .env-sample to .env first)."
            )
            return

        if no_input:
            self.stdout.write(
                f"\nSkipping .env update (--no-input). "
                f"You can set DB={db_url} in your .env file manually."
            )
            return

        if not update_env:
            if not sys.stdin.isatty():
                self.stdout.write(
                    f"\nNon-interactive mode: skipping .env update. "
                    f"You can set DB={db_url} in your .env file manually."
                )
                return
            answer = (
                input(
                    f"\nWould you like to update the DB setting in {env_path}\n"
                    f"to use the newly created database? [y/N] "
                )
                .strip()
                .lower()
            )
            if answer not in ("y", "yes"):
                self.stdout.write(
                    f"Skipped. You can set DB={db_url} in your .env file manually."
                )
                return

        # Write the updated .env, keeping a backup of the original
        backup_path = env_path.with_suffix(".env.bak")
        shutil.copy2(env_path, backup_path)
        self.stdout.write(f"Backed up {env_path} to {backup_path}")

        content = env_path.read_text()
        new_line = f"DB={db_url}"
        if re.search(r"^DB=", content, re.MULTILINE):
            content = re.sub(r"^DB=.*$", new_line, content, flags=re.MULTILINE)
        else:
            content = new_line + "\n" + content
        env_path.write_text(content)  # noqa: S606 - intentional dev-only .env update
        self.stdout.write(self.style.SUCCESS(f"Updated {env_path}"))
