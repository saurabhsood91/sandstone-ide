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
            res = self.fs.get_volume_details(volume_path)
            res = res.to_dict()
        # Otherwise list volumes
        else:
            res = self.volume_paths

        self.write(res)

    @sandstone.lib.decorators.authenticated
    def put(self, volume_path=None):
        """
        Provides move, copy, and rename functionality. An action must be
        specified when calling this method.
        """
        if not volume_path:
            raise tornado.web.HTTPError(400)
        elif volume_path not in self.volume_paths:
            raise tornado.web.HTTPError(404)

        action = self.get_argument('action',None)
        if not action:
            raise tornado.web.HTTPError(400)

        fp = action['data']['filepath']

        if action['action'] == 'move':
            newpath = action['data']['newpath']
            self.fs.move(fp,newpath)
            self.write({'msg':'File moved to {}'.format(newpath)})
        elif action['action'] == 'copy':
            newpath = action['data']['newpath']
            self.fs.copy(fp,newpath)
            self.write({'msg':'File copied to {}'.format(newpath)})
        elif action['action'] == 'rename':
            newpath = action['data']['newpath']
            self.fs.rename(fp,newpath)
            self.write({'msg':'File renamed to {}'.format(newpath)})
        else:
            raise tornado.web.HTTPError(400)

class FileHandler(BaseHandler,FSMixin):
    """
    This handler implements the file resource for the
    filesystem REST API. This resource resides under the
    volume resource.
    """

    @sandstone.lib.decorators.authenticated
    def get(self, filepath=None):
        """
        Get file details for the specified file.
        """
        if not filepath:
            raise tornado.web.HTTPError(400)
        elif not self.fs.exists(filepath):
            raise tornado.web.HTTPError(404)

        res = self.fs.get_file_details(filepath)
        res = res.to_dict()
        self.write(res)

    @sandstone.lib.decorators.authenticated
    def post(self, filepath=None):
        """
        Create a new file at the specified path.
        """
        if not filepath:
            raise tornado.web.HTTPError(400)

        self.fs.create_file(filepath)
        self.write({'msg':'File created at {}'.format(filepath)})

    @sandstone.lib.decorators.authenticated
    def put(self, filepath=None):
        """
        Change the group or permissions of the specified file. Action
        must be specified when calling this method.
        """
        if not filepath:
            raise tornado.web.HTTPError(400)
        elif not self.fs.exists(filepath):
            raise tornado.web.HTTPError(404)

        action = self.get_argument('action',None)
        if not action:
            raise tornado.web.HTTPError(400)

        if action['action'] == 'update_group':
            newgrp = action['data']['group']
            self.fs.update_group(filepath,newgrp)
            self.write({'msg':'Updated group for {}'.format(filepath)})
        elif action['action'] == 'update_permissions':
            newperms = action['data']['permissions']
            self.fs.update_permisions(filepath,newperms)
            self.write({'msg':'Updated permissions for {}'.format(filepath)})

    @sandstone.lib.decorators.authenticated
    def delete(self, filepath=None):
        """
        Delete the specified file.
        """
        if not filepath:
            raise tornado.web.HTTPError(400)
        elif not self.fs.exists(filepath):
            raise tornado.web.HTTPError(404)

        self.fs.delete_file(filepath)
        self.write({'msg':'File deleted at {}'.format(filepath)})

class DirectoryHandler(BaseHandler,FSMixin):
    """
    This handler implements the directory resource for the
    filesystem REST API. This resource resides under the
    volume resource.
    """

    @sandstone.lib.decorators.authenticated
    def get(self, filepath=None):
        """
        Get directory details for the specified file. If contents is
        set to True (default) then the directory contents will be sent
        along with the directory details. If dir_size is set to True
        (default=False) then du -hs will be run against subdirectories
        for accurate content sizes.
        """
        if not filepath:
            raise tornado.web.HTTPError(400)
        elif not self.fs.exists(filepath):
            raise tornado.web.HTTPError(404)

        contents = self.get_argument('contents', True)
        dir_sizes = self.get_argument('dir_sizes', False)

        res = self.fs.get_directory_details(filepath,contents=contents,dir_sizes=dir_sizes)
        res = res.to_dict()
        self.write(res)

    @sandstone.lib.decorators.authenticated
    def post(self, filepath=None):
        """
        Create a new directory at the specified path.
        """
        if not filepath:
            raise tornado.web.HTTPError(400)

        self.fs.create_directory(filepath)
        self.write({'msg':'Directory created at {}'.format(filepath)})

    @sandstone.lib.decorators.authenticated
    def put(self, filepath=None):
        """
        Change the group or permissions of the specified directory. Action
        must be specified when calling this method.
        """
        if not filepath:
            raise tornado.web.HTTPError(400)
        elif not self.fs.exists(filepath):
            raise tornado.web.HTTPError(404)

        action = self.get_argument('action',None)
        if not action:
            raise tornado.web.HTTPError(400)

        if action['action'] == 'update_group':
            newgrp = action['data']['group']
            self.fs.update_group(filepath,newgrp)
            self.write({'msg':'Updated group for {}'.format(filepath)})
        elif action['action'] == 'update_permissions':
            newperms = action['data']['permissions']
            self.fs.update_permisions(filepath,newperms)
            self.write({'msg':'Updated permissions for {}'.format(filepath)})

    @sandstone.lib.decorators.authenticated
    def delete(self, filepath=None):
        """
        Delete the specified directory.
        """
        if not filepath:
            raise tornado.web.HTTPError(400)
        elif not self.fs.exists(filepath):
            raise tornado.web.HTTPError(404)

        self.fs.delete_directory(filepath)
        self.write({'msg':'Directory deleted at {}'.format(filepath)})

class FileContentsHandler(BaseHandler, FSMixin):
    """
    This handler provides read and write functionality for file contents.
    """

    @sandstone.lib.decorators.authenticated
    def get(self, filepath=None):
        """
        Get the contents of the specified file.
        """
        if not filepath:
            raise tornado.web.HTTPError(400)
        elif not self.fs.exists(filepath):
            raise tornado.web.HTTPError(404)

        contents = self.fs.read_file(filepath)
        self.write({'filepath':filepath,'contents': contents})

    @sandstone.lib.decorators.authenticated
    def post(self, filepath=None):
        """
        Write the given contents to the specified file. This is not
        an append, all file contents will be replaced by the contents
        given.
        """
        if not filepath:
            raise tornado.web.HTTPError(400)
        elif not self.fs.exists(filepath):
            raise tornado.web.HTTPError(404)

        contents = self.get_argument('contents', None)
        if contents == None:
            raise tornado.web.HTTPError(400)

        self.fs.write_file(filepath, contents)
        self.write({'msg': 'Updated file at {}'.format(filepath)})
