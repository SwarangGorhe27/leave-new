from pathlib import Path
import uuid
# from celery import uuid
from django.core.files.storage import default_storage


def upload_leave_document(file):
    """
    Upload leave attachment and return metadata.

    Returns:
    {
        "file_name": str,
        "file_url": str,
        "file_type": str,
        "file_size_kb": int,
    }
    """

    storage_path = default_storage.save(
        f"leave_documents/"
        f"{uuid.uuid4()}{Path(file.name).suffix}",
        file,
    )
#Test the backend for file upload and metadata extraction in docs first then the UI on monday. This is a critical feature for leave applications and we need to ensure it works seamlessly before integrating it into the UI.
    return {
        "file_name": Path(file.name).name,
        "file_url": default_storage.url(storage_path),
        "file_type": getattr(file, "content_type", None),
        "file_size_kb": round(file.size / 1024),
    }