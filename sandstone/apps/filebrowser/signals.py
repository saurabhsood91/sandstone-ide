from pydispatch import dispatcher
import json
import tornado.escape
from sandstone.lib.websocket_client import WebSocketClient
from sandstone.lib.handlers.broadcast import BroadcastManager

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
    # ws = WebSocketClient(data=message)
    # ws.connect('ws://localhost:8888/messages')
    BroadcastManager.broadcast(message)


def filetree_expanded(sender):
    from posixfs import PosixFS
    filenode = sender['node']
    filepath = filenode['filepath']
    needs_dirs = sender['dirs']
    dir_contents = PosixFS.get_dir_contents(filepath)

    contents = []
    if needs_dirs:
        for node in dir_contents:
            if node[2]:
                contents.append({
                    'type': 'file',
                    'filepath': node[1],
                    'filename': node[0]
                })
    else:
        for node in dir_contents:
            if node[2]:
                filetype = 'dir'
            else:
                filetype = 'file'
            contents.append({
                'type': filetype,
                'filepath': node[1],
                'filename': node[0]
            })
    message = {
        'key': 'filetree:got_contents',
        'data': {
            'contents': contents,
            'node': filenode
        }
    }
    BroadcastManager.broadcast(message)

# Connect signals
dispatcher.connect(filetree_init, signal='filetree:init')

dispatcher.connect(filetree_expanded, signal='filetree:expanded')
