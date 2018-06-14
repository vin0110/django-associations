import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'associations',
    'tests',
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'fixtures'),
]
SECRET_KEY = 'zrxi&w6mvxocep5*s1&y)aai&uq3h0w7#huw#_7v5s)qsxci_#'
