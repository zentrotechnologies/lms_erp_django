from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminauth', '0004_faculty_and_permanent_address_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE adminauth_useradmin
                        ALTER COLUMN designation TYPE bigint
                        USING (CASE WHEN designation IS NOT NULL AND designation::text ~ '^[0-9]+$'
                                    THEN designation::bigint ELSE NULL END);
                    ALTER TABLE adminauth_useradmin
                        ALTER COLUMN city TYPE bigint
                        USING (CASE WHEN city IS NOT NULL AND city::text ~ '^[0-9]+$'
                                    THEN city::bigint ELSE NULL END);
                    ALTER TABLE adminauth_useradmin
                        ALTER COLUMN state TYPE bigint
                        USING (CASE WHEN state IS NOT NULL AND state::text ~ '^[0-9]+$'
                                    THEN state::bigint ELSE NULL END);
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='useradmin',
                    name='designation',
                    field=models.BigIntegerField(blank=True, null=True),
                ),
                migrations.AlterField(
                    model_name='useradmin',
                    name='city',
                    field=models.BigIntegerField(blank=True, db_index=True, null=True),
                ),
                migrations.AlterField(
                    model_name='useradmin',
                    name='state',
                    field=models.BigIntegerField(blank=True, db_index=True, null=True),
                ),
            ],
        ),
    ]