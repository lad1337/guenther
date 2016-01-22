from pathlib import Path

from appdirs import AppDirs
import pyaudio

app_dirs = AppDirs('Guenther')

DEFAUL_CONFIG = {
    'path': {
        'config': Path(app_dirs.user_config_dir) / 'guenther.ini',
        'samples': Path(app_dirs.user_data_dir) / 'samples/',
        'rules': Path(app_dirs.user_data_dir) / 'rules/'
    },
    'audio': {
        'sample_rate': (44100, int),
        'chunk_size': (4096, int),
        'channels': (1, int),
        'format': (pyaudio.paInt16, int)
    },
    'listen':{
        'interval': (2, int)
    }
}

ARGUMENT_MAP = {
    'debug': ('server', 'debug'),
    'config_path': ('path', 'config'),
    'rule_folder': ('path', 'rules'),
    'sample_folder': ('path', 'samples'),
    'listen_interval': ('listen', 'interval')
}
