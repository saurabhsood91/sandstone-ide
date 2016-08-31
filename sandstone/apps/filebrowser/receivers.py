from pydispatch import dispatcher
from posixfs import PosixFS

def filetree_init(sender):
    # get the list of root directories
    root_dirs = PosixFS.list_root_paths()
    # TODO send the data back to the client
