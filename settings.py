# Configuration file for mongoweb
# Wentao Han (wentao.han@gmail.com)

import os.path

import pymongo


debug = True

template_path = os.path.join(os.path.dirname(__file__), 'templates')

static_path = os.path.join(os.path.dirname(__file__), 'static')

db = pymongo.Connection().test


del os
del pymongo
