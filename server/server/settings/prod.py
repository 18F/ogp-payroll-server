import os

import dj_database_url

from .base import *

DATABASES = {'default': dj_database_url.config()}

SECRET_KEY = os.environ['SECRET_KEY']
