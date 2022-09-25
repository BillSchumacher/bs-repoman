import os
from pathlib import Path

BASE_PATH = Path(os.getcwd()).resolve()
HOME_PATH = Path.home()
CONFIG_PATH = HOME_PATH / '.config' / 'bs_repoman'
CONFIG_FILE_PATH = CONFIG_PATH / 'config.ini'
CACHE_PATH = HOME_PATH / '.cache' / 'bs_repoman'
GITHUB_TEMPLATES_PATH = CACHE_PATH / 'bs-repoman-github-templates'
GITHUB_TEMPLATES_PATH_ALL = GITHUB_TEMPLATES_PATH / 'all'
