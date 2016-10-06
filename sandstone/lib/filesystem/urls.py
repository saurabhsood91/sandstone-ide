from sandstone.lib.filesystem.handlers import VolumeHandler
from sandstone.lib.filesystem.handlers import FileHandler
from sandstone.lib.filesystem.handlers import DirectoryHandler



URL_SCHEMA = [
            (r"/a/filesystem/volumes/([^/]*)", VolumeHandler),
            (r"/a/filesystem/volumes/(.*)/directories/(.*)/", DirectoryHandler),
            (r"/a/filesystem/volumes/(.*)/files/(.*)/", FileHandler),
        ]
