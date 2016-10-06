import json
import tornado.web

import sandstone.lib.decorators
from sandstone import settings
from sandstone.lib.handlers.base import BaseHandler
from sandstone.lib.filesystem.mixins import FSMixin



class VolumeHandler(BaseHandler,FSMixin):
    """
    This handler implements the volume resource for the
    filesystem REST API.
    """

    @sandstone.lib.decorators.authenticated
    def get(self, volume_path=None):
        """
        If a volume path is passed, then return details for that volume.
        Otherwise, return a list of configured volumes.
        """
        # Volume specified
        if volume_path:
            if volume_path not in self.volume_paths:
                raise tornado.web.HTTPError(404)
            res = self.fs.get_volume_info(volume_path)
        # Otherwise list volumes
        else:
            res = self.volume_paths

        self.write(res)

class FileHandler(BaseHandler,FSMixin):
    """
    This handler implements the file resource for the
    filesystem REST API. This resource resides under the
    volume resource.
    """

    @sandstone.lib.decorators.authenticated
    def get(self, filepath):
        """

        """

class DirectoryHandler(BaseHandler,FSMixin):
    """
    This handler implements the directory resource for the
    filesystem REST API. This resource resides under the
    volume resource.
    """
    pass
