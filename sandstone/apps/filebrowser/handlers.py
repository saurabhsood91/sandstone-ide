import os
import re
import uuid
import json
import logging
import operator
import tornado.web
import tornado.ioloop
import tempfile

from tornado.concurrent import Future
from tornado import gen

import sandstone.lib.decorators
from sandstone import settings
from sandstone.lib.handlers.base import BaseHandler
from sandstone.apps.filebrowser.mixins.fs_mixin import FSMixin
from sandstone.lib.filewatcher import Filewatcher


class LocalFileHandler(BaseHandler,FSMixin):

    @sandstone.lib.decorators.authenticated
    def get(self, path):
        abspath = os.path.abspath(path)
        try:
            content = self.fs.read_file(abspath)
            self.write({
                'content':content
            })
        except:
            self.set_status(404)
            return

    @sandstone.lib.decorators.authenticated
    def post(self, path):
        is_dir = self.get_argument('isDir',False) == 'true'
        try:
            if is_dir:
                file_path = self.fs.create_directory(path)
            else:
                file_path = self.fs.create_file(path)
            self.write({
                'result':file_path+', created',
                'filepath':file_path
            })
        except:
            self.set_status(404)
            return

    @sandstone.lib.decorators.authenticated
    def put(self, path):
        content = json.loads(self.request.body)['content']
        try:
            file_path = self.fs.update_file(path,content)
            self.write({
                'result':file_path+', updated',
                'filepath':file_path
            })
        except:
            self.set_status(404)
            return

    @sandstone.lib.decorators.authenticated
    def delete(self, path):
        try:
            file_path = self.fs.delete_file(path)
            self.write({
                'result':file_path+', deleted',
                'filepath':file_path
            })
        except:
            self.set_status(404)
            return

class FilesystemUtilHandler(BaseHandler,FSMixin):

    @sandstone.lib.decorators.authenticated
    def get(self):
        operation = self.get_argument('operation')

        if operation=='CHECK_EXISTS':
            filepath = self.get_argument('filepath')
            result = self.fs.file_exists(filepath)
            self.write({'result':result})
        if operation=='GET_NEXT_UNTITLED_FILE':
            dirpath = self.get_argument('dirpath')
            index = 0
            fileExists = True
            while fileExists:
                index+=1
                filename = 'Untitled' + str(index)
                newFilePath = os.path.join(dirpath,filename)
                fileExists = self.fs.file_exists(newFilePath)
            self.write({'result':newFilePath})
        if operation=='GET_NEXT_UNTITLED_DIR':
            dirpath = self.get_argument('dirpath')
            index = 0
            dirExists = True
            while dirExists:
                index+=1
                dirname = 'UntitledFolder' + str(index)
                newDirPath = os.path.join(dirpath,dirname,'')
                dirExists = self.fs.file_exists(newDirPath)
            self.write({'result':newDirPath})
        if operation=='GET_NEXT_DUPLICATE':
            filepath = self.get_argument('filepath')
            isDir = os.path.isdir(filepath)
            index = 0
            fileExists = True
            while fileExists:
                index+=1
                if isDir:
                    newFilePath = ''.join([filepath[:-1],'-duplicate%s'%index,'/'])
                else:
                    newFilePath = ''.join([filepath,'-duplicate%s'%index])
                fileExists = self.fs.file_exists(newFilePath)
            self.write({'result':newFilePath})
        if operation == "GET_GROUPS":
            res = self.fs.get_groups()
            self.write(json.dumps(res))
        if operation == "GET_ROOT_DIR":
            # list_of_root_dirs = self.fs.list_root_paths(self.current_user)
            list_of_root_dirs = self.fs.list_root_paths()
            filepath = self.get_argument('filepath')
            root_dirs = []
            for root in list_of_root_dirs:
                if filepath.startswith(root):
                    root_dirs.append(root)
            sorted(root_dirs,key=len)
            self.write({'result': root_dirs[0]})
        if operation == 'GET_VOLUME_INFO':
            filepath = self.get_argument('filepath')
            res = self.fs.get_volume_info(filepath)
            self.write(json.dumps({'result': res}))

    @sandstone.lib.decorators.authenticated
    def post(self):
        operation = self.get_argument('operation')

        if operation=='RENAME':
            filepath = self.get_argument('filepath')
            new_name = self.get_argument('newFileName')
            if os.path.isdir(filepath):
                basepath = os.path.split(os.path.dirname(filepath))[0]
                newpath = os.path.join(basepath,new_name,'')
            else:
                basepath = os.path.dirname(filepath)
                newpath = os.path.join(basepath,new_name)
            result = self.fs.rename_file(filepath,newpath)
        elif operation=='COPY':
            origpath = self.get_argument('origpath')
            newpath = self.get_argument('newpath')
            result = self.fs.copy_file(origpath,newpath)
        elif operation=='CHANGE_PERMISSIONS':
            result = self.change_permissions()
        elif operation == 'CHANGE_GROUP':
            filepath = self.get_argument('filepath')
            group = self.get_argument('group')
            self.fs.change_group(filepath, group)
            result = "Changed Group"
        self.write({'result':result})

    @sandstone.lib.decorators.authenticated
    def change_permissions(self):
        perm_string = self.get_argument('permissions')
        filepath = self.get_argument('filepath')
        self.fs.change_permisions(filepath, perm_string)
        result = (filepath, perm_string)
        return result

@tornado.web.stream_request_body
class SimpleUploadHandler(BaseHandler, FSMixin):

    @tornado.web.authenticated
    def post(self):
        fp = self.request.headers['Uploaddir']
        dest_path = os.path.join(fp,self.filename)
        self.fd.close()
        # shutil.move(self.fd.name,dest_path)
        self.fs.move_file(self.fd.name, dest_path)
        os.chmod(dest_path, 0644)

    @tornado.web.authenticated
    def prepare(self):
        self.tmp_cache = ''
        self.stream_started = False
        self.request.connection.set_max_body_size(2*1024**3)
        fd_info = tempfile.mkstemp()
        self.fd = open(fd_info[1],'w')

    def data_received(self, data):
        self.tmp_cache += data
        pdata = self._process(data)
        self.fd.write(pdata)

    def _process(self, data):
        trimmed = data.splitlines()
        tmp = data.splitlines(True)

        if not self.stream_started:
            self.boundary = trimmed[0].strip()
            tmp = tmp[1:]
            trimmed = trimmed[1:]
            self.stream_started = True

            try:
                first_elem = trimmed[:5].index("")
                metadata = trimmed[:first_elem]
                self.filename = metadata[0].split(';')[-1].split('=')[-1][1:-1]
                tmp = tmp[first_elem + 1:]
                trimmed = trimmed[first_elem + 1:]
            except ValueError:
                pass

        try:
            last_elem = trimmed.index(self.boundary + "--")
            self.stream_started = False
            return "".join(tmp[:last_elem - 1])
        except ValueError:
            return "".join(tmp)

class FileTreeHandler(BaseHandler,FSMixin):

    @sandstone.lib.decorators.authenticated
    def get(self):
        is_folders = self.get_argument('folders', '')
        if is_folders == "true":
            self.get_folders()
        else:
            dirpath = self.get_argument('dirpath','')
            dir_contents = []
            if dirpath == '':
                for r in self.fs.list_root_paths():
                    dir_contents.append({
                        'type':'dir',
                        'filename':r,
                        'filepath':r})
            else:
                for i in self.fs.get_dir_contents(dirpath):
                    if os.path.isdir(i['filepath']):
                        i['type'] = 'dir'
                    else:
                        i['type'] = 'file'
                    i['is_accessible'] = os.access(i['filepath'], os.W_OK)
                    dir_contents.append(i)
                Filewatcher.add_directory_to_watch(dirpath)
            self.write(json.dumps(dir_contents))

    @sandstone.lib.decorators.authenticated
    def get_folders(self):
        dirpath = self.get_argument('dirpath','')
        dir_contents = []
        if dirpath == '':
            for r in self.fs.list_root_paths():
                dir_contents.append({
                    'type':'dir',
                    'filename':r,
                    'filepath':r})
        else:
            for i in self.fs.get_dir_folders(dirpath):
                folder = {
                    'filename': i[0],
                    'filepath': i[1],
                }
                if os.path.isdir(i[1]):
                    folder['type'] = 'dir'
                else:
                    folder['type'] = 'file'
                dir_contents.append(folder)
            Filewatcher.add_directory_to_watch(dirpath)
        self.write(json.dumps(dir_contents))
