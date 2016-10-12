import os
import pwd
import urllib
import mock
import json
import tempfile
import shutil
import stat
import subprocess
from sandstone.lib.handlers.base import BaseHandler
from sandstone.lib.test_utils import TestHandlerBase

from sandstone.lib.filesystem.handlers import VolumeHandler



EXEC_USER = pwd.getpwuid(os.getuid())[0]

class VolumeHandlerTestCase(TestHandlerBase):
    def setUp(self,*args,**kwargs):
        self.test_dir = tempfile.mkdtemp()
        super(VolumeHandlerTestCase,self).setUp(*args,**kwargs)

    def tearDown(self,*args,**kwargs):
        shutil.rmtree(self.test_dir)
        super(VolumeHandlerTestCase,self).tearDown(*args,**kwargs)

    def test_get_unauthed(self):
        response = self.fetch(
            '/a/filesystem/volumes/',
            method='GET',
            follow_redirects=False)

        self.assertEqual(response.code, 302)
        self.assertTrue(response.headers['Location'].startswith('/auth/login?next=%2F'))
