from receivers import *
from pydispatch import dispatcher

# TODO This seems a little redundant
# TODO find a better way
SIGNALS_HANDLED = (
    'filetree:init',
)

dispatcher.connect(filetree_init, signal='filetree:init')

dispatcher.connect(filetree_expanded, signal='filetree:expanded')
