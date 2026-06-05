from django.core.exceptions import ValidationError
import datetime

def validate_export_filters(from_date: datetime.date = None, to_date: datetime.date = None) -> None:
    """Validate export filters, particularly date ranges."""
    if from_date and to_date:
        if from_date > to_date:
            raise ValidationError("from_date cannot be after to_date.")
            
def validate_import_file_extension(filename: str) -> None:
    """Validate that the import file has an allowed extension."""
    allowed_extensions = ['.csv', '.xlsx']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError(f"Invalid file format. Allowed formats are: {', '.join(allowed_extensions)}")
