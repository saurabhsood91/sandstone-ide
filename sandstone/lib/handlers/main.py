import os
import datetime
import tornado.web
import sandstone.lib.decorators
from sandstone.lib.handlers.base import BaseHandler



class MainHandler(BaseHandler):

    @sandstone.lib.decorators.authenticated
    def get(self):
        ctx = {}
        self.render('lib/templates/sandstone.html', **ctx)
