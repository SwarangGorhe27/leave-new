from django.db import migrations


def seed_attendance_tracking_modes(apps, schema_editor):
    """Seed default attendance tracking modes."""
    AttendanceTrackingMode = apps.get_model('attendance', 'AttendanceTrackingMode')
    
    tracking_modes = [
        {"code": "MANUAL", "label": "Manual Entry"},
        {"code": "BIOMETRIC", "label": "Biometric"},
        {"code": "GPS", "label": "GPS Based"},
        {"code": "SYSTEM", "label": "System Generated"},
        {"code": "MOBILE", "label": "Mobile App"},
        {"code": "WEB", "label": "Web Portal"},
    ]
    
    for mode in tracking_modes:
        AttendanceTrackingMode.objects.get_or_create(
            code=mode["code"],
            defaults={"label": mode["label"], "is_active": True}
        )


def reverse_seed(apps, schema_editor):
    """Remove seeded tracking modes."""
    AttendanceTrackingMode = apps.get_model('attendance', 'AttendanceTrackingMode')
    codes = ["MANUAL", "BIOMETRIC", "GPS", "SYSTEM", "MOBILE", "WEB"]
    AttendanceTrackingMode.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_add_attendance_tracking_mode'),
    ]

    operations = [
        migrations.RunPython(seed_attendance_tracking_modes, reverse_seed),
    ]

