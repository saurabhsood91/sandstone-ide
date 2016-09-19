import unittest
from pydispatch import dispatcher
from sandstone.lib.broadcast.manager import BroadcastManager
from sandstone.lib.broadcast.message import BroadcastMessage
import mock

MOCK_ROOT_DIRS = ['/home/saurabh', '/tmp']

MOCK_CONTENTS = [
    ('file1', '/home/saurabh/file1', False),
    ('dir1', '/home/saurabh/dir1', True)
]

class SignalTestCase(unittest.TestCase):
    """
    Tests the dispatch handlers
    """

    @mock.patch('sandstone.apps.filebrowser.posixfs.PosixFS.list_root_paths')
    def test_filetree_init(self, mock_function):
        mock_function.return_value = MOCK_ROOT_DIRS

        with mock.patch('sandstone.apps.filebrowser.signals.BroadcastManager.broadcast') as mock_broadcast:

            message = {
                'key': 'filetree:init',
                'data': {}
            }
            bmsg = BroadcastMessage.create_from_dict(message)
            dispatcher.send(bmsg.key, bmsg.data)

            message = {
                'key': 'filetree:root_dirs',
                'data': {
                    'root_dirs': [
                        {
                            'type': 'dir',
                            'filepath': '/home/saurabh',
                            'filename': '/home/saurabh'
                        },
                        {
                            'type': 'dir',
                            'filepath': '/tmp',
                            'filename': '/tmp'
                        }
                    ]
                }
            }
            try:
                bmsg = BroadcastMessage.create_from_dict(message)
            except BroadcastMessage.MessageValidationError:
                return

            mock_broadcast.assert_called()
            # get call arguments
            args = mock_broadcast.call_args
            # key and data should be equal
            self.assertEqual(bmsg.key, args[0][0].key)
            self.assertEqual(bmsg.data, args[0][0].data)

    @mock.patch('sandstone.apps.filebrowser.posixfs.PosixFS.get_dir_contents')
    def test_filetree_expanded_files(self, mock_get_dir_contents):
        mock_get_dir_contents.return_value = MOCK_CONTENTS

        with mock.patch('sandstone.apps.filebrowser.signals.BroadcastManager.broadcast') as mock_broadcast:
            # get contents including directories and files
            message = {
                'key': 'filetree:expanded',
                'data': {
                    'node': {
                        'filepath': '/home/saurabh',
                    },
                    'dirs': False
                },
            }
            bmsg = BroadcastMessage.create_from_dict(message)
            dispatcher.send(bmsg.key, bmsg.data)

            message = {
                'key': 'filetree:got_contents',
                'data': {
                    'contents': [
                        {
                            'type': 'file',
                            'filepath': '/home/saurabh/file1',
                            'filename': 'file1'
                        },
                        {
                            'type': 'dir',
                            'filepath': '/home/saurabh/dir1',
                            'filename': 'dir1'
                        }
                    ],
                    'node': {
                        'filepath': '/home/saurabh'
                    }
                }
            }

            try:
                bmsg = BroadcastMessage.create_from_dict(message)
            except BroadcastMessage.MessageValidationError:
                return

            mock_broadcast.assert_called()
            args = mock_broadcast.call_args

            self.assertEqual(bmsg.key, args[0][0].key)
            self.assertEqual(bmsg.data, args[0][0].data)

    @mock.patch('sandstone.apps.filebrowser.posixfs.PosixFS.get_dir_contents')
    def test_filetree_expanded_contents(self, mock_get_dir_contents):
        mock_get_dir_contents.return_value = MOCK_CONTENTS

        with mock.patch('sandstone.apps.filebrowser.signals.BroadcastManager.broadcast') as mock_broadcast:
            # get only the directories
            message = {
                'key': 'filetree:expanded',
                'data': {
                    'node': {
                        'filepath': '/home/saurabh',
                    },
                    'dirs': True
                },
            }
            bmsg = BroadcastMessage.create_from_dict(message)
            dispatcher.send(bmsg.key, bmsg.data)

            message = {
                'key': 'filetree:got_contents',
                'data': {
                    'contents': [
                        {
                            'type': 'dir',
                            'filepath': '/home/saurabh/dir1',
                            'filename': 'dir1'
                        }
                    ],
                    'node': {
                        'filepath': '/home/saurabh'
                    }
                }
            }

            try:
                bmsg = BroadcastMessage.create_from_dict(message)
            except BroadcastMessage.MessageValidationError:
                return

            mock_broadcast.assert_called()
            args = mock_broadcast.call_args

            # check for data and key being equal
            self.assertEqual(bmsg.key, args[0][0].key)
            self.assertEqual(bmsg.data, args[0][0].data)
