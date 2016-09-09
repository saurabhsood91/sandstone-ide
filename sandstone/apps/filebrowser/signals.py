from pydispatch import dispatcher
from websocket import create_connection
import json
import tornado.escape
from sandstone.lib.websocket_client import WebSocketClient

# TODO This seems a little redundant
# TODO find a better way
SIGNALS_HANDLED = (
    'filetree:init',
)



# Receivers
def filetree_init(sender):
    from posixfs import PosixFS
    # get the list of root directories
    root_paths = PosixFS.list_root_paths()
    root_nodes = []
    for r in root_paths:
        root_nodes.append({
            'type': 'dir',
            'filepath': r,
            'filename': r
        })
    message = {
        'key': 'filetree:root_dirs',
        'data': {
            'root_dirs': root_nodes
        }
    }
    ws = WebSocketClient(data=message)
    ws.connect('ws://localhost:8888/messages')

def filetree_expanded(sender):
    print sender
    print 'Filetree Expanded'

# Connect signals
dispatcher.connect(filetree_init, signal='filetree:init')

dispatcher.connect(filetree_expanded, signal='filetree:expanded')
