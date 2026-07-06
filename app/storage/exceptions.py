# Filesystem

# FileNotFoundError
# PermissionError
# OSError

#         │
#         ▼

# LocalStorage

#         │
#         ▼

# Storage Exceptions

# ObjectNotFound
# StorageError
# StoragePermissionDenied

class StorageError(Exception):
    pass
class ObjectNotFound(StorageError):
    pass
class ObjectAlreadyExists(StorageError):
    pass
class StorageUnavailable(StorageError):
    pass
class StoragePermissionDenied(StorageError):
    pass
class FileError(Exception):
    pass
class FileNotFound(FileError):
    pass
class FileAccessDenied(FileError):
    pass
class AuthenthicationError(Exception):
    pass
class InvalidToken(AuthenthicationError):
    pass
class UploadError(Exception):
    pass
class UploadedSessionExpired(UploadError):
    pass
class ChuckAlreadyUploaded(UploadError):
    pass
class UploasAlreadyCompleted(UploadError):
    pass
class UploadSessionNotFound(Exception):
    pass
class UploadIncomplete(Exception):
    pass