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