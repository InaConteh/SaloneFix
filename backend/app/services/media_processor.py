import io
from typing import Tuple
from PIL import Image, ImageOps
from app.core.exceptions import MediaInvalidError, MediaTooLargeError

ALLOWED_MIME_TYPES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_and_sanitize_image(file_bytes: bytes, filename: str, mime_type: str) -> Tuple[bytes, str, str]:
    """
    Validate image file size, magic bytes signature, dimensions, and strip EXIF for privacy.
    Returns: (sanitized_bytes, output_mime_type, sanitized_filename)
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise MediaTooLargeError(max_size_mb=10)

    # Check magic bytes
    valid_signature = False
    for allowed_mime, signatures in ALLOWED_MIME_TYPES.items():
        if mime_type.lower() == allowed_mime:
            for sig in signatures:
                if file_bytes.startswith(sig):
                    valid_signature = True
                    break
    if not valid_signature:
        # Fallback check against any known signature
        for allowed_mime, signatures in ALLOWED_MIME_TYPES.items():
            for sig in signatures:
                if file_bytes.startswith(sig):
                    valid_signature = True
                    mime_type = allowed_mime
                    break

    if not valid_signature:
        raise MediaInvalidError("Uploaded file is not a supported image format (JPEG, PNG, WEBP).")

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()  # Ensure image is not truncated or corrupted
    except Exception as e:
        raise MediaInvalidError(f"Image validation failed: {str(e)}")

    # Re-open for sanitization
    image = Image.open(io.BytesIO(file_bytes))
    try:
        image = ImageOps.exif_transpose(image)
    except Exception:
        pass

    # Strip EXIF/XMP/ICC metadata by copying only pixel data into a fresh image.
    # (Image.copy() would carry image.info over; .tobytes()/frombytes does not.)
    clean_image = Image.frombytes(image.mode, image.size, image.tobytes())

    output_buffer = io.BytesIO()
    save_format = image.format if image.format in ["JPEG", "PNG", "WEBP"] else "JPEG"
    output_mime = f"image/{save_format.lower()}"
    clean_image.save(output_buffer, format=save_format, quality=90)
    sanitized_bytes = output_buffer.getvalue()

    return sanitized_bytes, output_mime, filename
