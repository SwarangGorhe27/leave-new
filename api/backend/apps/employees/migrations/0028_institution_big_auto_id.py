import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0027_education_master_aishe_core"),
    ]

    operations = [
        migrations.AlterField(
            model_name="institution",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="employeeeducation",
            name="institution",
            field=models.ForeignKey(
                blank=True,
                db_column="institution_id",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="emp_education_records",
                to="employees.institution",
            ),
        ),
        migrations.RunSQL(
            sql=(
                "ALTER SEQUENCE IF EXISTS mst_institution_id_seq "
                "AS bigint NO MAXVALUE;"
            ),
            reverse_sql=(
                "ALTER SEQUENCE IF EXISTS mst_institution_id_seq "
                "AS integer MAXVALUE 32767;"
            ),
        ),
    ]
