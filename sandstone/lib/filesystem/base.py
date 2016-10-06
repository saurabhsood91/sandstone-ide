class FilesystemObject:
    """
    This object standardizes the representation of filesystem objects handled by
    the filesystem REST API. FilesystemObject handles validation, as well as
    serialization.
    """
    class ObjectValidationError(Exception):
        pass

    def __init__(self, **kwargs):
        obj_fp = kwargs.get('filepath', None)
        obj_type = kwargs.get('type', None)
        if not obj_fp and obj_type:
            raise self.MessageValidationError(
                "'filepath' and 'type' must both be defined"
            )

class FilesystemBaseClass:
    """
    Base class inherited by all filesystem interfaces. The required methods here
    are used by the filesystem REST API.
    """

    def file_exists(self, filepath):
        raise NotImplementedError('Method not implemented')

    def create_file(self, filepath):
        raise NotImplementedError('Method not implemented')

    def read_file(self, filepath):
        raise NotImplementedError('Method not implemented')

    def update_file(self, filepath, content):
        raise NotImplementedError('Method not implemented')

    def delete_file(self, filepath):
        raise NotImplementedError('Method not implemented')

    def create_directory(self, filepath):
        raise NotImplementedError('Method not implemented')

    def move_file(self, origpath, newpath):
        raise NotImplementedError('Method not implemented')

    def copy_file(self, origpath, newpath):
        raise NotImplementedError('Method not implemented')

    def rename_file(self, origpath, newpath):
        raise NotImplementedError('Method not implemented')

    def list_root_paths(self, **kwargs):
        raise NotImplementedError('Method not implemented')

    def get_permissions(self, perm_string):
        raise NotImplementedError('Method not implemented')

    def get_dir_contents(self, dirpath):
        raise NotImplementedError('Method not implemented')

    def get_dir_folders(self, dirpath):
        raise NotImplementedError('Method not implemented')

    def change_permisions(self, filepath, perm_string):
        raise NotImplementedError('Method not implemented')

    def get_groups(self,a):
        raise NotImplementedError('Method not implemented')

    def change_group(self, filepath, group_name):
        raise NotImplementedError('Method not implemented')

    def get_volume_info(self, filepath):
        raise NotImplementedError('Method not implemented')

    def get_size(self, filepath):
        raise NotImplementedError('Method not implemented')
