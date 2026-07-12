from http import HTTPStatus

class URLShortenerException(Exception):
    """Base class for exceptions"""

    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)

class ValidationError(URLShortenerException):
    """Exception raised for validation errors."""
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST

class ConflictError(URLShortenerException):
    """Exception raised for conflicts, such as duplicate entries."""
    status_code: HTTPStatus = HTTPStatus.CONFLICT

class ResourceNotFoundError(URLShortenerException):
    """Exception raised when a requested resource is not found."""
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND

class InvalidAliasError(ValidationError):
    detail = "Invalid alias."


class InvalidExpirationError(ValidationError):
    detail = "Expiration time must be in the future."


class AliasAlreadyExistsError(ConflictError):
    def __init__(self, alias: str):
        super().__init__(f"Alias '{alias}' already exists.")

class URLNotFoundError(ResourceNotFoundError):
    detail = "Short URL not found."