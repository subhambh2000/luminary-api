class LuminaryException(Exception):
    """Base class for all exceptions raised by this application"""
    status_code: int
    error_type: str

    def __init__(self, status_code: int, error_type: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.error_type = error_type


class CollectionNotFoundException(LuminaryException):
    def __init__(self, message: str):
        super().__init__(
            status_code=404,
            error_type="CollectionNotFound",
            message=message)


class IngestException(LuminaryException):
    def __init__(self, message: str):
        super().__init__(
            status_code=500,
            error_type="IngestException",
            message=message)


class RetrievalException(LuminaryException):
    def __init__(self, message: str):
        super().__init__(
            status_code=500,
            error_type="RetrievalException",
            message=message)
