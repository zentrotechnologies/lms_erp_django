from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminauth', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS current_status varchar(50) NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS work_group varchar(100) NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS work_category varchar(100) NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS pf_no varchar(100) NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS pan_number varchar(250) NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS adhar_number varchar(250) NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS bank_name varchar(250) NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS account_number varchar(250) NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS permanent_address_line_one text NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS permanent_address_line_two text NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS permanent_country bigint NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS permanent_state varchar(150) NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS permanent_city varchar(150) NULL;"
                        "ALTER TABLE adminauth_useradmin ADD COLUMN IF NOT EXISTS permanent_pincode varchar(20) NULL;"
                    ),
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='useradmin',
                    name='current_status',
                    field=models.CharField(blank=True, max_length=50, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='work_group',
                    field=models.CharField(blank=True, max_length=100, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='work_category',
                    field=models.CharField(blank=True, max_length=100, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='pf_no',
                    field=models.CharField(blank=True, max_length=100, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='pan_number',
                    field=models.CharField(blank=True, max_length=250, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='adhar_number',
                    field=models.CharField(blank=True, max_length=250, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='bank_name',
                    field=models.CharField(blank=True, max_length=250, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='account_number',
                    field=models.CharField(blank=True, max_length=250, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='permanent_address_line_one',
                    field=models.TextField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='permanent_address_line_two',
                    field=models.TextField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='permanent_country',
                    field=models.BigIntegerField(blank=True, db_index=True, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='permanent_state',
                    field=models.CharField(blank=True, max_length=150, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='permanent_city',
                    field=models.CharField(blank=True, max_length=150, null=True),
                ),
                migrations.AddField(
                    model_name='useradmin',
                    name='permanent_pincode',
                    field=models.CharField(blank=True, max_length=20, null=True),
                ),
            ],
        ),
    ]