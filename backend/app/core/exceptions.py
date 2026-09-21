from fastapi import HTTPException, status


class SaloneFixException(HTTPException):
    def __init__(self, status_code: int, error_code: str, message: str, details: dict = None):
        super().__init__(
            status_code=status_code,
            detail={"error_code": error_code, "message": message, "details": details or {}},
        )


class ValidationError(SaloneFixException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class UnauthorizedError(SaloneFixException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            message=message,
        )


class ForbiddenError(SaloneFixException):
    def __init__(self, message: str = "Permission denied for this operation or resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            message=message,
        )


class NotFoundError(SaloneFixException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=f"{resource} not found",
        )


class StateConflictError(SaloneFixException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="STATE_CONFLICT",
            message=message,
            details=details,
        )


class MediaInvalidError(SaloneFixException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="MEDIA_INVALID",
            message=message,
        )


class MediaTooLargeError(SaloneFixException):
    def __init__(self, max_size_mb: int = 10):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            error_code="MEDIA_TOO_LARGE",
            message=f"Uploaded file exceeds maximum limit of {max_size_mb} MB",
        )


class RateLimitedError(SaloneFixException):
    def __init__(self, retry_after_seconds: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMITED",
            message=f"Rate limit exceeded. Please wait {retry_after_seconds} seconds before trying again.",
            details={"retry_after_seconds": retry_after_seconds},
        )


class DependencyUnavailableError(SaloneFixException):
    def __init__(self, dependency: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="DEPENDENCY_UNAVAILABLE",
            message=f"{dependency} is not available. The human-only workflow continues without it.",
            details={"dependency": dependency},
        )
