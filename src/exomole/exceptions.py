class APIError(Exception):
    pass


class LineCommentError(Exception):
    pass


class LineValueError(Exception):
    pass


class LineWarning(UserWarning):
    pass


class AllParseError(Exception):
    pass


class AllParseWarning(UserWarning):
    pass


class DefParseError(Exception):
    pass


class DataParseError(Exception):
    pass


class StatesParseError(DataParseError):
    pass


class TransParseError(DataParseError):
    pass
