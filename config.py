import json
import os
import logging

class Config(object):
    def __init__(self, config_file, default_config):
        self.config_file = config_file
        self.log = logging.getLogger('root')
        self.cfg = self._read_config_file()
        if None is self.cfg:
            self.log.info('No config file found, creating default config %s',
                          self.config_file)
            self.cfg = default_config
            self.save_config(self.cfg)
            pass
        # Generate getters for all config properties
        for prop in self.cfg.keys():
            setattr(self.__class__, prop, self._get_option_getter_func(prop))
            pass
        pass

    def _read_config_file(self):
        cfg = None
        try:
            with open(self.config_file) as f:
                cfg = json.load(f)
                pass
            pass
        except IOError as e:
            self.log.warning('Unable to open config file %s: %s',
                             self.config_file, str(e))
            pass
        return cfg

    def save_config(self, cfg=None):
        if cfg is None:
            cfg = self.cfg
            pass
        try:
            with open(self.config_file, 'w') as f:
                json.dump(cfg, f, indent=True)
                pass
            pass
        except IOError as e:
            self.log.error('Error saving config file %s: %s',
                           self.config_file, str(e))
            pass
        pass

    def _get_option_getter_func(self, option_key):
        return property(lambda self : self._get_option(option_key))

    def _get_option(self, key):
        if key in self.cfg:
            value = self.cfg[key]
            self.log.debug('Read config option: %s = %s',
                           key, str(value))
            return value
        else:
            self.log.error('Config option "%s" not found', key)
            return None

class DwarfConfig(Config):

    DEFAULT_CONFIG = {
      }

    def __init__(self, config_file):
        super(DwarfConfig, self).__init__(config_file, self.DEFAULT_CONFIG)
        pass
