"""School related background tasks."""
import structlog
from celery import shared_task

logger = structlog.get_logger(__name__)

@shared_task(name="school.resize_logo")
def resize_school_logo(school_id: str, path: str) -> None:
    """
    Dummy task to resize the school logo.
    In a real app, this would download from R2, use Pillow to resize, and re-upload.
    """
    logger.info("Resizing school logo", school_id=school_id, path=path)
    # 1. Download from R2 using StorageService
    # 2. Resize to 512x512
    # 3. Upload back to R2
    # 4. Update school.logo_url in DB if necessary
    logger.info("Successfully resized school logo", school_id=school_id)
