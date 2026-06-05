from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0004_seed_attendance_tracking_modes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shiftdefinition",
            name="break_mins",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Default unpaid break deducted when no lunch punches are available.",
            ),
        ),
    ]
