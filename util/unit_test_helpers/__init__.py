""" Helper utilities for writing unit tests in Apros """

from mock import patch


class ApplyPatchMixin(object):
    """
    Mixin with patch helper method
    """

    def apply_patch(self, *args, **kwargs):
        """
        Applies patch and registers a callback to stop the patch in TearDown method
        """
        patcher = patch(*args, **kwargs)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock
