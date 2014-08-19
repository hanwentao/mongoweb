# Configuration file for mongoweb
# Wentao Han (wentao.han@gmail.com)

import os.path


debug = True

template_path = os.path.join(os.path.dirname(__file__), 'templates')

static_path = os.path.join(os.path.dirname(__file__), 'static')


del os
