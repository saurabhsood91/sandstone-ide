import tornado.web
from sandstone.lib.filesystem.manager import VolumeManager
from sandstone.lib.filesystem.interfaces.posixfs import PosixFS



class FSMixin(tornado.web.RequestHandler):

    def initialize(self):
        self.fs = PosixFS()
        self.volume_paths = VolumeManager.get_volume_paths()
