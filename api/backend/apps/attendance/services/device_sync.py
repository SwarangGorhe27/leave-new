from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from apps.attendance.models import AttendanceDevice


@dataclass
class DeviceSyncSummary:
    created: int
    updated: int
    errors: list[str]


def sync_devices(
    company_id,
    validated_devices: list[dict],
) -> DeviceSyncSummary:

    created = 0
    updated = 0
    errors = []

    if not validated_devices:
        return DeviceSyncSummary(
            created=0,
            updated=0,
            errors=[],
        )

    existing_devices = {
        device.device_code: device
        for device in AttendanceDevice.objects.filter(
            company_id=company_id,
            device_code__in=[
                d["device_code"]
                for d in validated_devices
            ],
        )
    }

    create_objects = []
    update_objects = []

    with transaction.atomic():

        for device_data in validated_devices:

            device_code = device_data["device_code"]

            existing = existing_devices.get(device_code)

            if existing:

                existing.device_name = device_data["device_name"]
                existing.door_address = device_data.get("door_address")
                existing.device_type = device_data.get("device_type")

                existing.meta_data = device_data.get(
                    "meta_data",
                    {},
                )

                existing.last_sync_at = timezone.now()

                update_objects.append(existing)

            else:

                create_objects.append(
                    AttendanceDevice(
                        company_id=company_id,
                        device_code=device_code,
                        device_name=device_data["device_name"],
                        door_address=device_data.get(
                            "door_address"
                        ),
                        device_type=device_data.get(
                            "device_type"
                        ),
                        meta_data=device_data.get(
                            "meta_data",
                            {},
                        ),
                        is_trusted=True,
                        last_sync_at=timezone.now(),
                    )
                )

        if create_objects:
            AttendanceDevice.objects.bulk_create(
                create_objects,
                batch_size=500,
            )
            created = len(create_objects)

        if update_objects:
            AttendanceDevice.objects.bulk_update(
                update_objects,
                [
                    "device_name",
                    "door_address",
                    "device_type",
                    "meta_data",
                    "last_sync_at",
                ],
                batch_size=500,
            )
            updated = len(update_objects)

    return DeviceSyncSummary(
        created=created,
        updated=updated,
        errors=errors,
    )