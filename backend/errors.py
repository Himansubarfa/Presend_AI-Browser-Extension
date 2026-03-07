class APIError(Exception):
    """Base class for API errors."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or {})
        rv['message'] = self.message
        return rv

class TextTooLongError(APIError):
    def __init__(self, max_length):
        super().__init__(
            message=f"Text exceeds maximum length of {max_length} characters",
            status_code=413
        )

class InvalidJSONError(APIError):
    def __init__(self):
        super().__init__(
            message="Request must be JSON with Content-Type: application/json",
            status_code=400
        )

class MissingTextFieldError(APIError):
    def __init__(self):
        super().__init__(
            message="Missing 'text' field in JSON",
            status_code=400
        )

class ProcessingError(APIError):
    def __init__(self, detail=None):
        msg = "Text processing failed" + (f": {detail}" if detail else "")
        super().__init__(message=msg, status_code=422)