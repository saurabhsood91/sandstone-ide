from pydispatch import dispatcher
# from posixfs import PosixFS

def filetree_init(sender):
    pass
    # get the list of root directories
    # root_dirs = PosixFS.list_root_paths()
    # TODO send the data back to the client

def filetree_expanded(sender):
    print sender
    print 'Filetree Expanded'
