from pydispatch import dispatcher


# TODO This seems a little redundant
# TODO find a better way
SIGNALS_HANDLED = (
    'filetree:init',
)


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
dispatcher.connect(filetree_init, signal='filetree:init')

dispatcher.connect(filetree_expanded, signal='filetree:expanded')
