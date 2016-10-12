class FilesystemBaseClass:
    """
    Base class inherited by all filesystem interfaces. The required methods here
    are used by the filesystem REST API.
    """

    fs_type = None

    def get_volume_details(self, volume_path):
        raise NotImplementedError('Method not implemented')

    def get_groups(self, volume_path):
        raise NotImplementedError('Method not implemented')

    def get_file_details(self, filepath):
        raise NotImplementedError('Method not implemented')

    def get_directory_details(self, filepath):
        raise NotImplementedError('Method not implemented')

    def exists(self, filepath):
        raise NotImplementedError('Method not implemented')

    def get_type_from_path(self, filepath):
        raise NotImplementedError('Method not implemented')

    def get_size(self, filepath):
        raise NotImplementedError('Method not implemented')

    def create_file(self, filepath):
        raise NotImplementedError('Method not implemented')

    def read_file(self, filepath):
        raise NotImplementedError('Method not implemented')

    def write_file(self, filepath, content, dir_sizes):
        raise NotImplementedError('Method not implemented')

    def delete(self, filepath):
        raise NotImplementedError('Method not implemented')

    def create_directory(self, filepath):
        raise NotImplementedError('Method not implemented')

    def move(self, origpath, newpath):
        raise NotImplementedError('Method not implemented')

    def copy(self, origpath, newpath):
        raise NotImplementedError('Method not implemented')

    def rename(self, origpath, newpath):
        raise NotImplementedError('Method not implemented')

    def update_permissions(self, filepath, perm_string):
        raise NotImplementedError('Method not implemented')

    def update_group(self, filepath, new_group):
        raise NotImplementedError('Method not implemented')
