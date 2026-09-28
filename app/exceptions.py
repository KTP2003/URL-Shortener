from http import HTTPStatus

class URLShortenerException(Exception):
    """Base class for exceptions"""

    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)

class ValidationError(URLShortenerException):
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST

class ConflictError(URLShortenerException):
    status_code: HTTPStatus = HTTPStatus.CONFLICT

class ResourceNotFoundError(URLShortenerException):
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

class URLExpiredError(URLShortenerException):
    status_code = HTTPStatus.GONE
    detail = "Short URL has expired."