class DomainError(Exception):
    http_status_code: int = 400

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class NotFoundError(DomainError):
    http_status_code = 404


class ConflictError(DomainError):
    http_status_code = 409


class ValidationError(DomainError):
    http_status_code = 422
