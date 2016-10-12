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
from sandstone.lib.filesystem.schemas import VolumeObject
from sandstone.lib.filesystem.schemas import FilesystemObject
from sandstone.lib.filesystem.manager import VolumeManager



class PosixFS(FilesystemBaseClass):
    """
    Interface for a Posix filesystem.
    """

    fs_type = 'posix'

    # Extra methods

    # Base methods
    def get_volume_details(self, volume_path):
        details = {
            'type': 'volume',
            'name': volume_path,
            'fs_type': fs_type
        }
        # get usage details
        p = subprocess.Popen(['df', '-h', filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        size, used, avail, used_pct = out.split()[-5:-1]
        details.update({
            'used': used,
            'available': avail,
            'used_pct': float(used_pct.strip('%')),
            'size': size
        })
        # get groups
        groups = self.get_groups(volume_path)
        details.update({
            'groups': groups
        })
        volume = VolumeObject(**details)
        return volume

    def get_groups(self, volume_path):
        groups = subprocess.check_output(["id", "--name", "-G"]).strip().split()
        return groups

    def _parse_ls_line(self, out):
        contents = out.split()
        perms = contents[1]
        t = 'file'
        if perms[0] == 'd':
            t = 'directory'
        perms = perms[1:]
        owner = contents[3]
        group = contents[4]
        size = contents[5]
        if not size[-1].isalpha():
            size += 'b'
        details = {
            'type': t,
            'permissions': perms,
            'owner': owner,
            'group': group,
            'size': size
        }
        return details

    def get_file_details(self, filepath):
        volpath = VolumeManager.get_volume_from_path(filepath)
        filepath = os.path.abspath(filepath)
        dirname, name = os.path.split(filepath)
        details = {
            'volume': volpath,
            'filepath': filepath,
            'dirpath': dirname,
            'name': name
        }
        p = subprocess.Popen(['ls', '-lsah', filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        ls_det = self._parse_ls_line(out)
        details.update(ls_det)
        file_details = FilesystemObject(**details)
        return file_details

    def get_directory_details(self, filepath, contents=True, dir_sizes=False):
        filepath = os.path.abspath(filepath)
        dirname, name = os.path.split(filepath)
        volpath = VolumeManager.get_volume_from_path(filepath)
        details = {
            'filepath': filepath,
            'volume': volpath,
            'dirpath': dirname,
            'name': name
        }
        if not contents:
            p = subprocess.Popen(['ls', '-lsahd', filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            ls_det = self._parse_ls_line(out)
            details.update(ls_det)
            dir_details = FilesystemObject(**details)
            return dir_details
        else:
            # Otherwise, get dir contents
            p = subprocess.Popen(['ls', '-lsah', filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            lines = out.split('\n')[1:]
            # the directory details
            ls_det = self._parse_ls_line(lines[0])
            details.update(ls_det)
            # directory contents
            contents = []
            for line in lines[2:-1]:
                line_details = self._parse_ls_line(line)
                name = line.split()[-1]
                fp = os.path.join(filepath,name)
                line_details.update({
                    'name': name,
                    'dirpath': filepath,
                    'volume': volpath,
                    'filepath': fp
                })
                if dir_sizes and line_details['type'] == 'directory':
                    line_details['size'] = self.get_size(fp)
                file_details = FilesystemObject(**line_details)
                contents.append(file_details)

            details['contents'] = contents

        dir_details = FilesystemObject(**details)
        return dir_details

    def exists(self, filepath):
        filepath = os.path.abspath(filepath)
        exists = os.path.exists(filepath)
        return exists

    def get_type_from_path(self, filepath):
        if os.path.isdir(filepath):
            return 'directory'
        return 'file'

    def get_size(self, filepath):
        filepath = os.path.abspath(filepath)
        p = subprocess.Popen(['du','-hs',filepath],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        out = out.strip()
        size, fp = out.split('\t')
        if not size[-1].isalpha():
            size += 'b'
        return size

    def create_file(self, filepath):
        filepath = os.path.abspath(filepath)
        if os.path.exists(filepath):
            logging.info('File {} already exists, not creating'.format(filepath))
            return filepath
        fd = open(filepath,'w')
        fd.close()

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

    def delete(self, filepath):
        filepath = os.path.abspath(filepath)
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        else:
            os.remove(filepath)

    def create_directory(self, filepath):
        filepath = os.path.abspath(filepath)
        os.makedirs(filepath)

    def move(self, origpath, newpath):
        origpath = os.path.abspath(origpath)
        newpath = os.path.abspath(newpath)
        shutil.move(origpath,newpath)

    def copy(self, origpath, newpath):
        origpath = os.path.abspath(origpath)
        newpath = os.path.abspath(newpath)
        if os.path.isdir(origpath):
            shutil.copytree(origpath,newpath)
        else:
            shutil.copy2(origpath,newpath)

    def rename(self, origpath, newpath):
        origpath = os.path.abspath(origpath)
        newpath = os.path.abspath(newpath)
        os.rename(origpath,newpath)

    def update_permisions(filepath, perm_string):
        os.chmod(filepath, int(perm_string, 8))

    def update_group(self, filepath, group_name):
        # Get uid
        uid = os.stat(filepath).st_uid
        # Get GID of new group
        gid = grp.getgrnam(group_name).gr_gid
        # change group
        os.chown(filepath, uid, gid)
