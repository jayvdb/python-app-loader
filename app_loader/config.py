

from importlib import import_module
from django.utils import six
from .versions import get_versions
from .spec import CONF_SPEC
import warnings
from .utils import merge


class Config(dict):

    """Simple Module Config Object
    encapsulation of dot access dictionary

    use dictionary as constructor

    """

    def get_value(self, key, values):
        '''Accept key of propery and actual values'''
        return merge(values, self.get_property(key))

    def get_property(self, key):
        """Expect Django Conf property"""
        _key = DJANGO_CONF[key]
        return getattr(self, _key, CONF_SPEC[_key])

    @property
    def module_name(self):
        """Module name from module if is set"""
        if hasattr(self, "module"):
            return self.module.__name__
        return None

    @property
    def name(self):
        """Distribution name from module if is set"""
        if hasattr(self, "module"):
            return self.module.__name__.replace('_', '-')
        return None

    @property
    def version(self):
        """return module version"""
        return get_versions([self.module_name]).get(self.module_name, None)

    def set_module(self, module):
        """Just setter for module"""
        setattr(self, "module", module)

    def __getattr__(self, attr):
        return self.get(attr, None)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class MasterConfig(object):

    """Simple Module Config Object
    encapsulation of dot access dictionary

    use dictionary as constructor

    """

    def __init__(self, loaded_modules, config_spec, use_cache=True, *args, **kwargs):
        self.modules = loaded_modules
        self.config_spec = config_spec
        self._config = {}
        self.use_cache = use_cache
        super(MasterConfig, self).__init__(*args, **kwargs)

    def __getattr__(self, attr):
        '''merge all items or returns default by spec
        '''

        # use cached values
        if self.use_cache and attr in self._config:
            return self._config[attr]

        if attr not in self.config_spec.keys():
            raise KeyError('You tries to access key {}'
                           ' which is not declared in spec {}'.format(
                               attr,
                               ', '.join(self.config_spec.keys())))

        default_value = self.config_spec.get(attr, None)

        items = default_value

        for mod, config in self.modules:
            # TODO get default from config spec
            _items = getattr(config, attr, default_value)
            items = merge(items, _items)

        if self.use_cache:
            self._config[attr] = items

        return items