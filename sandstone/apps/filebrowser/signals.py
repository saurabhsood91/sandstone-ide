<<<<<<< d9ef475f0c0c98504a25860476c0720a7a6f3ac8
=======
from receivers import *
>>>>>>> Fixed circular dependency.
from pydispatch import dispatcher

# TODO This seems a little redundant
# TODO find a better way
SIGNALS_HANDLED = (
    'filetree:init',
)

<<<<<<< d9ef475f0c0c98504a25860476c0720a7a6f3ac8
# Receivers
def filetree_init(sender):
    from posixfs import PosixFS
    # get the list of root directories
    root_dirs = PosixFS.list_root_paths()
    # TODO send the data back to the client

def filetree_expanded(sender):
    print sender
    print 'Filetree Expanded'

# Connect signals
=======
>>>>>>> Fixed circular dependency.
dispatcher.connect(filetree_init, signal='filetree:init')

dispatcher.connect(filetree_expanded, signal='filetree:expanded')
