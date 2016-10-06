import tornado.web
from sandstone.lib.filesystem.interfaces.posixfs import PosixFS



class FSMixin(tornado.web.RequestHandler):

    def initialize(self):
        self.fs = PosixFS()
        self.volume_paths = self.fs.list_root_paths()
