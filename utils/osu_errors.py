class OsuBaseException(Exception):
    """Base Exception For Osu Errors"""
    pass

    

class NoUserFound(OsuBaseException):
    """Returns An Exception For When An User Isn't Found"""
    pass