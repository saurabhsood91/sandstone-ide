import unittest
import mock
from sandstone.lib.test_utils import TestHandlerBase

from sandstone.lib.filesystem.interfaces.posixfs import PosixFS
from sandstone.lib.filesystem.mixins import FSMixin



ROOTS = (
    '/tmp/test/',
    '/testdir/',
)


class FSMixinTestCase(TestHandlerBase):
    def test_initialize(self):
        with mock.patch('sandstone.lib.filesystem.manager.VolumeManager.volumes',list(ROOTS)):
            request = mock.Mock()
            handler = FSMixin(self.get_app(),request)
            self.assertTrue(isinstance(handler.fs,PosixFS))
            self.assertEqual(handler.volume_paths,list(ROOTS))
