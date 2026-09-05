from django.db import migrations


class Migration(migrations.Migration):

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE master_educationalqualifications "
                "ADD COLUMN IF NOT EXISTS status boolean NOT NULL DEFAULT true;"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]