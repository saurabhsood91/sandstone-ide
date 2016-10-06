import abc



class FilesystemBaseClass(metaclass=abc.ABCMeta):
    """
    Abstract base class inherited by all filesystem interfaces. The required methods here
    are used by the filesystem REST API.
    """

    @classmethod
    def _isDelegatableIdentifier(cls, methodName):
        return not methodName.startswith('_')

    @classmethod
    def _getMethods(cls, aClass):
        names  = sorted(dir(aClass), key=str.lower)
        attrs  = [(n, getattr(aClass, n)) for n in names if cls._isDelegatableIdentifier(n)]
        return dict((n, a) for n, a in attrs if inspect.ismethod(a))

    @classmethod
    def _getMethodDeclaration(cls, aMethod):
        try:
            name = aMethod.__name__
            spec = inspect.getargspec(aMethod)
            args = inspect.formatargspec(spec.args, spec.varargs, spec.keywords, spec.defaults)
            return '%s%s' % (name, args)
        except TypeError, e:
            return '%s(cls, ...)' % (name)

    @classmethod
    def _checkImplementation(cls, aImplementation):
        """
        the implementation must implement at least all methods of this abstract base class,
        unless the methods is private ('_xxxx()'); also check signature (must be identical).
        @param aImplementation: implementing object
        """
        missing = {}

        ours   = cls._getMethods(cls)
        theirs = cls._getMethods(aImplementation)

        for name, method in ours.iteritems():
            if not (theirs.has_key(name)):
                missing[name + "()"] = "not implemented"
                continue

            ourf   = cls._getMethodDeclaration(method)
            theirf = cls._getMethodDeclaration(theirs[name])

            if not (ourf == theirf):
                missing[name + "()"] = "method signature differs"

        if not (len(missing) == 0):
            raise Exception('incompatible Implementation-implementation %s: %s' % (aImplementation.__class__.__name__, missing))

    def __init__(self, *args, **kwargs):
        self.__class__._checkImplementation(FilesystemBaseClass)

    @abc.abstractmethod
    def file_exists(self, filepath):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def create_file(self, filepath):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def read_file(self, filepath):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def update_file(self, filepath, content):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def delete_file(self, filepath):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def create_directory(self, filepath):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def move_file(self, origpath, newpath):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def copy_file(self, origpath, newpath):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def rename_file(self, origpath, newpath):
        raise NotImplementedError('Method not implemented')

    def list_root_paths(self, **kwargs):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def get_permissions(self, perm_string):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def get_dir_contents(self, dirpath):
        raise NotImplementedError('Method not implemented')

    def get_dir_folders(self, dirpath):
        raise NotImplementedError('Method not implemented')

    def change_permisions(self, filepath, perm_string):
        raise NotImplementedError('Method not implemented')

    def get_groups(self):
        raise NotImplementedError('Method not implemented')

    def change_group(self, filepath, group_name):
        raise NotImplementedError('Method not implemented')

    def get_volume_info(self, filepath):
        raise NotImplementedError('Method not implemented')

    @abc.abstractmethod
    def get_size(self, filepath):
        raise NotImplementedError('Method not implemented')
