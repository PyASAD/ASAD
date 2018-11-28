import ConfigParser

#===============================================================================

DEFAULT_CONFIG_FILE = "default.conf"

class GlobalConfig(object):

    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(config_file)

    @staticmethod
    def get_base_method(name):
        lst = name.split('_')
        base = lst[0]
        value = '_'.join(lst[1:])
        return base, value

    @property
    def config(self):
        return self._config
    @config.setter
    def config(self, value):
        self._config = value

    def __getitem__(self, key):
        base, value = GlobalConfig.get_base_method(key)
        return self.config.get(base, value)

    def __setitem__(self, key, val):
        base, value = GlobalConfig.get_base_method(key)
        return self.config.set(base, value, val)

    def write(self, out):
        self.config.write(out)

    def write_config_file(self, config_file=DEFAULT_CONFIG_FILE):
        with open(config_file, 'wb') as cfgf:
            self.config.write(cfgf)


#===============================================================================
