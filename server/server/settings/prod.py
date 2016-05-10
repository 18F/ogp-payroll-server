import os
from .base import *

import dj_database_url

DATABASES = {'default': dj_database_url.config()}

SECRET_KEY = os.environ['SECRET_KEY']
