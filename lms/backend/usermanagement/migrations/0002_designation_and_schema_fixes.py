from django.db import migrations


def apply_schema_changes(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        # 1. Dedicated designation table (idempotent - table may already exist
        #    from out-of-band setup on some environments).
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usermanagement_designation (
                id bigserial NOT NULL PRIMARY KEY,
                role_code varchar(50) NOT NULL UNIQUE,
                role_name varchar(100) NOT NULL,
                description text NULL,
                is_active boolean NOT NULL DEFAULT true,
                "createdAt" timestamptz NOT NULL DEFAULT now(),
                "updatedAt" timestamptz NULL,
                "createdBy" varchar(255) NULL,
                "updatedBy" varchar(255) NULL
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS usermanagement_designation_role_code_idx "
            "ON usermanagement_designation (role_code)"
        )

        # 2. Ensure is_parent_training_center has a DB default so user inserts
        #    never fail with a NOT NULL violation when the field is omitted.
        cursor.execute(
            "ALTER TABLE adminauth_useradmin "
            "ALTER COLUMN is_parent_training_center SET DEFAULT false"
        )

        # 3. ClassGroup.semester_ids must be jsonb for the @> lookup to work.
        cursor.execute(
            "ALTER TABLE master_classgroup "
            "ALTER COLUMN semester_ids TYPE jsonb USING semester_ids::jsonb"
        )


def revert(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0001_initial'),
        ('adminauth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(apply_schema_changes, revert),
    ]
