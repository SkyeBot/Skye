class OsuBaseException(Exception):
    """Base Exception For Osu Errors"""



class NoUserFound(OsuBaseException):
    """Returns An Exception For When An User Isn't Found"""



class NoBeatMapFound(OsuBaseException):
    """Returns an exception for when an beatmap/beatmapset isn't found"""

