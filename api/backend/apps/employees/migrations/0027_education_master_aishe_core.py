import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0026_bank_branch_details"),
    ]

    operations = [
        migrations.AlterField(
            model_name="institution",
            name="code",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="institution",
            name="label",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="university",
            name="code",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="university",
            name="label",
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name="institution",
            name="institution_type",
            field=models.CharField(
                choices=[
                    ("COLLEGE", "College"),
                    ("STANDALONE", "Standalone Institute"),
                ],
                default="COLLEGE",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="institution",
            name="university",
            field=models.ForeignKey(
                blank=True,
                db_column="university_id",
                help_text="Required only for colleges. Empty for standalone institutes.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="institutions",
                to="employees.university",
            ),
        ),
        migrations.AddField(
            model_name="institution",
            name="state",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="institution",
            name="district",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="institution",
            name="location",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="institution",
            name="college_type",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="institution",
            name="standalone_type",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="institution",
            name="management",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="institution",
            name="university_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="institution",
            name="university_type",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="university",
            name="state",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="university",
            name="district",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="university",
            name="location",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="university",
            name="university_type",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddIndex(
            model_name="institution",
            index=models.Index(fields=["label"], name="idx_mst_institution_label"),
        ),
        migrations.AddIndex(
            model_name="institution",
            index=models.Index(
                fields=["institution_type"], name="idx_mst_institution_type"
            ),
        ),
        migrations.AddIndex(
            model_name="institution",
            index=models.Index(
                fields=["university"], name="idx_mst_institution_university"
            ),
        ),
        migrations.AddIndex(
            model_name="institution",
            index=models.Index(
                fields=["state", "district"], name="idx_mst_institution_state_dist"
            ),
        ),
        migrations.AddIndex(
            model_name="university",
            index=models.Index(fields=["label"], name="idx_mst_university_label"),
        ),
        migrations.AddIndex(
            model_name="university",
            index=models.Index(
                fields=["state", "district"], name="idx_mst_university_state_dist"
            ),
        ),
    ]
