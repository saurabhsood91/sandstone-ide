import os
import sys
import stat
import pwd
import shutil
import logging
from sandstone import settings
import grp
import subprocess
from sandstone.lib.filesystem.base import FilesystemBaseClass



class PosixFS(FilesystemBaseClass):
    def file_exists(self, filepath):
        filepath = os.path.abspath(filepath)
        exists = os.path.exists(filepath)
        return exists

    def create_file(self, filepath):
        filepath = os.path.abspath(filepath)
        if os.path.exists(filepath):
            logging.info('File {} already exists, not creating'.format(filepath))
            return filepath
        fd = open(filepath,'w')
        fd.close()
        logging.info('Created file at {}'.format(filepath))
        return filepath

    def read_file(self, filepath):
        filepath = os.path.abspath(filepath)
        with open(filepath, 'r') as f:
            content = f.read()
        return content

    def update_file(self, filepath, content):
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            raise IOError
        with open(filepath, 'w') as local_file:
            for line in content:
                local_file.write(line.encode('utf8'))
        return filepath

    def delete_file(self, filepath):
        filepath = os.path.abspath(filepath)
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        else:
            os.remove(filepath)
        return filepath

    def create_directory(self, filepath):
        filepath = os.path.abspath(filepath)
        os.makedirs(filepath)
        return filepath

    def move_file(self, origpath, newpath):
        origpath = os.path.abspath(origpath)
        newpath = os.path.abspath(newpath)
        shutil.move(origpath,newpath)
        return newpath

    def copy_file(self, origpath, newpath):
        origpath = os.path.abspath(origpath)
        newpath = os.path.abspath(newpath)
        if os.path.isdir(origpath):
            shutil.copytree(origpath,newpath)
        else:
            shutil.copy2(origpath,newpath)
        return newpath

    def rename_file(self, origpath, newpath):
        origpath = os.path.abspath(origpath)
        newpath = os.path.abspath(newpath)
        os.rename(origpath,newpath)
        return newpath

    def list_root_paths(self, **kwargs):
        root_patterns = settings.FILESYSTEM_ROOT_DIRECTORIES
        formatted_patterns = []
        for patt in root_patterns:
            fmt = os.path.expandvars(patt)
            formatted_patterns.append(fmt)
        return formatted_patterns

    def get_permissions(self, perm_string):
        perms = []
        count = 0
        p = 0
        for i in perm_string[1:]:
            if i == 'r':
                p += 4
            elif i == 'w':
                p += 2
            elif i == 'x':
                p += 1
            if count == 2:
                perms.append('%d' % p)
                count = 0
                p = 0
            else:
                count += 1
        return ''.join(perms)

    def get_dir_contents(self, dirpath):

        dir_contents = []

        p = subprocess.Popen(['ls', '-lsah', dirpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = p.communicate()

        contents = out.split('\n')[1:]

        for node in contents:
            parts = node.split()
            if len(parts) == 0:
                continue
            if parts[-1] != '.' and parts[-1] != '..':
                filepath = os.path.join(dirpath, parts[-1])

                if os.path.isdir(filepath):
                    size = PosixFS.get_size(filepath)
                else:
                    size = parts[5]
                    if not size[-1].isalpha():
                        size = size + ' bytes'

                dir_contents.append({
                    'size': size,
                    'perm': parts[1],
                    'perm_string': PosixFS.get_permissions(parts[1]),
                    'owner': parts[3],
                    'group': parts[4],
                    'filepath': filepath,
                    'filename': parts[-1]
                    })
        return dir_contents

    def get_dir_folders(self, dirpath):
        contents = []
        for i in os.listdir(dirpath):
            filepath = os.path.join(dirpath,i)
            is_dir = os.path.isdir(filepath)
            if is_dir:
                filepath = filepath + '/'
            else:
                continue
            contents.append( ( i,filepath,is_dir ) )
        contents.sort(key=lambda tup: tup[1])
        return contents

    def change_permisions(filepath, perm_string):
        os.chmod(filepath, int(perm_string, 8))

    def get_groups(self):
        return subprocess.check_output(["id", "--name", "-G"]).strip().split()

    def change_group(self, filepath, group_name):
        # Get uid
        uid = os.stat(filepath).st_uid
        # Get GID of new group
        gid = grp.getgrnam(group_name).gr_gid
        # change group
        os.chown(filepath, uid, gid)

    def get_volume_info(filepath):
        df = subprocess.Popen(['df', filepath], stdout=subprocess.PIPE)
        output = df.communicate()[0]
        device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
        size = int(size) / (1024 * 1024)
        used = int(used) / (1024 * 1024)
        return {'percent': float(percent.strip('%')), 'used': used, 'size': size}

    def get_size(self, filepath):
        p = subprocess.Popen(
            ['du', '-hs', filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out = p.communicate()
        size = out[0].split('\t')[0]
        if size == '0':
            return '0.0K'
        return size
