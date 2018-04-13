"""Custom exceptions."""


class NoSuchDirectory(Exception):
    """Raise when a directory does not exist."""
    pass


class NoFilesFound(Exception):
    """Raise when no matching files are found."""
    pass


class PermissionDenied(Exception):
    """Raise when permission is denied."""
    pass


class ProcTimeout(Exception):
    """Raise when a process times out."""
    pass
