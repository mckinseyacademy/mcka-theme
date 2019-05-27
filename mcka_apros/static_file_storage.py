from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.core.exceptions import SuspiciousFileOperation


class NonStrictManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """
    Subclass to disable strict mode which raises ValueError
    for a non-existent file
    """
    manifest_strict = False

    def hashed_name(self, name, content=None, filename=None):
        try:
            return super(NonStrictManifestStaticFilesStorage, self).hashed_name(name, content, filename)
        except (ValueError, SuspiciousFileOperation):
            return name
