class RevelioException(Exception):
    pass


class AuthenticationError(RevelioException):
    pass


class AuthorizationError(RevelioException):
    pass


class ResourceNotFoundError(RevelioException):
    pass


class InvalidStateTransitionError(RevelioException):
    pass


class MissingCancellationNoteError(RevelioException):
    pass


class InactiveUserError(RevelioException):
    pass
