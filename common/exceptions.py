class DefaultException(Exception):
    """
    Default error class.
    """
    pass


class PostponedError(DefaultException):
    """
    Raised during postponed match parsing
    """
    def __init__(self, message="No goals found. The match might be postponed."):
        super().__init__(message)


class CaptchaError(DefaultException):
    """
    Raised when parsing fails due to CAPTCHA appearing on the page.
    """
    def __init__(self, message="Failed to parse stats. Likely due to CAPTCHA."):
        super().__init__(message)