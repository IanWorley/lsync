# Copyright 2017, Inderpreet Singh, All rights reserved.

import configparser
from typing import Dict
from io import StringIO
import collections
from distutils.util import strtobool
from abc import ABC
from typing import Type, TypeVar, Callable, Any
from regex import match

from .error import AppError
from .persist import Persist, PersistError
from .types import overrides


class ConfigError(AppError):
    """
    Exception indicating a bad config value
    """

    pass


InnerConfigType = Dict[str, str]
OuterConfigType = Dict[str, InnerConfigType]


# Source: https://stackoverflow.com/a/39205612/8571324
T = TypeVar("T", bound="InnerConfig")


class Converters:
    @staticmethod
    def null(_: T, __: str, value: str) -> str:
        return value

    @staticmethod
    def int(cls: T, name: str, value: str) -> int:
        if not value:
            raise ConfigError("Bad config: {}.{} is empty".format(cls.__name__, name))
        try:
            val = int(value)
        except ValueError:
            raise ConfigError(
                "Bad config: {}.{} ({}) must be an integer value".format(
                    cls.__name__, name, value
                )
            )
        return val

    @staticmethod
    def bool(cls: T, name: str, value: str) -> bool:
        if not value:
            raise ConfigError("Bad config: {}.{} is empty".format(cls.__name__, name))
        try:
            val = bool(strtobool(value))
        except ValueError:
            raise ConfigError(
                "Bad config: {}.{} ({}) must be a boolean value".format(
                    cls.__name__, name, value
                )
            )
        return val


class Checkers:
    @staticmethod
    def null(_: T, __: str, value: Any) -> Any:
        return value

    @staticmethod
    def string_nonempty(cls: T, name: str, value: str) -> str:
        if not value or not value.strip():
            raise ConfigError("Bad config: {}.{} is empty".format(cls.__name__, name))
        return value

    @staticmethod
    def int_non_negative(cls: T, name: str, value: int) -> int:
        if value < 0:
            raise ConfigError(
                "Bad config: {}.{} ({}) must be zero or greater".format(
                    cls.__name__, name, value
                )
            )
        return value

    @staticmethod
    def int_positive(cls: T, name: str, value: int) -> int:
        if value < 1:
            raise ConfigError(
                "Bad config: {}.{} ({}) must be greater than 0".format(
                    cls.__name__, name, value
                )
            )
        return value

    @staticmethod
    def string_vaild_hostname(
        cls: T, name: str, value: str
    ) -> str:  ##TODO: make sure that these validates a hostname steal from the frontend
        if not value or not value.strip() or not is_valid_hostname(value):
            raise ConfigError(
                "Bad config: {} {} has an invalid entry".format(cls.__name__, name)
            )
        return value


def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


class InnerConfig(ABC):
    """
    Abstract base class for a config section
    Config values are exposed as properties. They must be set using their native type.
    Internal utility methods are provided to convert strings to native types. These are
    only used when creating config from a dict.

    Implementation details:
    Each property has associated with is a checker and a converter function.
    The checker function performs boundary check on the native type value.
    The converter function converts the string representation into the native type.
    """

    class PropMetadata:
        """Tracks property metadata"""

        def __init__(self, checker: Callable, converter: Callable):
            self.checker = checker
            self.converter = converter

    # Global map to map a property to its metadata
    # Is there a way for each concrete class to do this separately?
    __prop_addon_map = collections.OrderedDict()

    @classmethod
    def _create_property(
        cls, name: str, checker: Callable, converter: Callable
    ) -> property:
        # noinspection PyProtectedMember
        prop = property(
            fget=lambda s: s._get_property(name),
            fset=lambda s, v: s._set_property(name, v, checker),
        )
        prop_addon = InnerConfig.PropMetadata(checker=checker, converter=converter)
        InnerConfig.__prop_addon_map[prop] = prop_addon
        return prop

    def _get_property(self, name: str) -> Any:
        return getattr(self, "__" + name, None)

    def _set_property(self, name: str, value: Any, checker: Callable):
        # Allow setting to None for the first time
        if value is None and self._get_property(name) is None:
            setattr(self, "__" + name, None)
        else:
            setattr(self, "__" + name, checker(self.__class__, name, value))

    @classmethod
    def from_dict(cls: Type[T], config_dict: InnerConfigType) -> T:
        """
        Construct and return inner config from a dict
        Dict values can be either native types, or str representations
        :param config_dict:
        :return:
        """
        config_dict = dict(config_dict)  # copy that we can modify

        # Loop over all the property name, and set them to the value given in config_dict
        # Raise error if a matching key is not found in config_dict
        # noinspection PyCallingNonCallable
        inner_config = cls()
        property_map = {
            p: getattr(cls, p)
            for p in dir(cls)
            if isinstance(getattr(cls, p), property)
        }
        for name, prop in property_map.items():
            if name not in config_dict:
                raise ConfigError("Missing config: {}.{}".format(cls.__name__, name))
            inner_config.set_property(name, config_dict[name])
            del config_dict[name]

        # Raise error if a key in config_dict did not match a property
        extra_keys = config_dict.keys()
        if extra_keys:
            raise ConfigError(
                "Unknown config: {}.{}".format(cls.__name__, next(iter(extra_keys)))
            )

        return inner_config

    def as_dict(self) -> InnerConfigType:
        """
        Return the dict representation of the inner config
        :return:
        """
        config_dict = collections.OrderedDict()
        cls = self.__class__
        my_property_to_name_map = {
            getattr(cls, p): p
            for p in dir(cls)
            if isinstance(getattr(cls, p), property)
        }
        # Arrange prop names in order of creation. Use the prop map to get the order
        # Prop map contains all properties of all config classes, so filtering is required
        all_properties = InnerConfig.__prop_addon_map.keys()
        for prop in all_properties:
            if prop in my_property_to_name_map.keys():
                name = my_property_to_name_map[prop]
                config_dict[name] = getattr(self, name)
        return config_dict

    def has_property(self, name: str) -> bool:
        """
        Returns true if the given property exists, false otherwise
        :param name:
        :return:
        """
        try:
            return isinstance(getattr(self.__class__, name), property)
        except AttributeError:
            return False

    def set_property(self, name: str, value: Any):
        """
        Set a property dynamically
        Do a str conversion of the value, if necessary
        :param name:
        :param value:
        :return:
        """
        cls = self.__class__
        prop_addon = InnerConfig.__prop_addon_map[getattr(cls, name)]
        # Do the conversion if value is of type str
        native_value = (
            prop_addon.converter(cls, name, value) if type(value) is str else value
        )
        # Set the property, which will invoke the checker
        # noinspection PyProtectedMember
        self._set_property(name, native_value, prop_addon.checker)


# Useful aliases
IC = InnerConfig
# noinspection PyProtectedMember
PROP = InnerConfig._create_property


class Config(Persist):
    """
    Configuration registry
    """

    class General(IC):
        debug = PROP("debug", Checkers.null, Converters.bool)
        verbose = PROP("verbose", Checkers.null, Converters.bool)

        def __init__(self):
            super().__init__()
            self.debug = None
            self.verbose = None

    class Lftp(IC):
        remote_address = PROP(
            "remote_address", Checkers.string_vaild_hostname, Converters.null
        )
        remote_username = PROP(
            "remote_username", Checkers.string_nonempty, Converters.null
        )
        remote_password = PROP(
            "remote_password", Checkers.string_nonempty, Converters.null
        )
        remote_port = PROP("remote_port", Checkers.int_positive, Converters.int)
        remote_path = PROP("remote_path", Checkers.string_nonempty, Converters.null)
        local_path = PROP("local_path", Checkers.string_nonempty, Converters.null)
        remote_path_to_scan_script = PROP(
            "remote_path_to_scan_script", Checkers.string_nonempty, Converters.null
        )
        use_ssh_key = PROP("use_ssh_key", Checkers.null, Converters.bool)
        num_max_parallel_downloads = PROP(
            "num_max_parallel_downloads", Checkers.int_positive, Converters.int
        )
        num_max_parallel_files_per_download = PROP(
            "num_max_parallel_files_per_download", Checkers.int_positive, Converters.int
        )
        num_max_connections_per_root_file = PROP(
            "num_max_connections_per_root_file", Checkers.int_positive, Converters.int
        )
        num_max_connections_per_dir_file = PROP(
            "num_max_connections_per_dir_file", Checkers.int_positive, Converters.int
        )
        num_max_total_connections = PROP(
            "num_max_total_connections", Checkers.int_non_negative, Converters.int
        )
        use_temp_file = PROP("use_temp_file", Checkers.null, Converters.bool)

        def __init__(self):
            super().__init__()
            self.remote_address = None
            self.remote_username = None
            self.remote_password = None
            self.remote_port = None
            self.remote_path = None
            self.local_path = None
            self.remote_path_to_scan_script = None
            self.use_ssh_key = None
            self.num_max_parallel_downloads = None
            self.num_max_parallel_files_per_download = None
            self.num_max_connections_per_root_file = None
            self.num_max_connections_per_dir_file = None
            self.num_max_total_connections = None
            self.use_temp_file = None

    class Controller(IC):
        interval_ms_remote_scan = PROP(
            "interval_ms_remote_scan", Checkers.int_positive, Converters.int
        )
        interval_ms_local_scan = PROP(
            "interval_ms_local_scan", Checkers.int_positive, Converters.int
        )
        interval_ms_downloading_scan = PROP(
            "interval_ms_downloading_scan", Checkers.int_positive, Converters.int
        )
        extract_path = PROP("extract_path", Checkers.string_nonempty, Converters.null)
        use_local_path_as_extract_path = PROP(
            "use_local_path_as_extract_path", Checkers.null, Converters.bool
        )

        def __init__(self):
            super().__init__()
            self.interval_ms_remote_scan = None
            self.interval_ms_local_scan = None
            self.interval_ms_downloading_scan = None
            self.extract_path = None
            self.use_local_path_as_extract_path = None

    class Web(InnerConfig):
        port = PROP("port", Checkers.int_positive, Converters.int)

        def __init__(self):
            super().__init__()
            self.port = None

    class AutoQueue(InnerConfig):
        enabled = PROP("enabled", Checkers.null, Converters.bool)
        patterns_only = PROP("patterns_only", Checkers.null, Converters.bool)
        auto_extract = PROP("auto_extract", Checkers.null, Converters.bool)

        def __init__(self):
            super().__init__()
            self.enabled = None
            self.patterns_only = None
            self.auto_extract = None

    def __init__(self):
        self.general = Config.General()
        self.lftp = Config.Lftp()
        self.controller = Config.Controller()
        self.web = Config.Web()
        self.autoqueue = Config.AutoQueue()

    @staticmethod
    def _check_section(dct: OuterConfigType, name: str) -> InnerConfigType:
        if name not in dct:
            raise ConfigError("Missing config section: {}".format(name))
        val = dct[name]
        del dct[name]
        return val

    @staticmethod
    def _check_empty_outer_dict(dct: OuterConfigType):
        extra_keys = dct.keys()
        if extra_keys:
            raise ConfigError("Unknown section: {}".format(next(iter(extra_keys))))

    @classmethod
    @overrides(Persist)
    def from_str(cls: "Config", content: str) -> "Config":
        config_parser = configparser.ConfigParser()
        try:
            config_parser.read_string(content)
        except (configparser.MissingSectionHeaderError, configparser.ParsingError) as e:
            raise PersistError(
                "Error parsing Config - {}: {}".format(type(e).__name__, str(e))
            )
        config_dict = {}
        for section in config_parser.sections():
            config_dict[section] = {}
            for option in config_parser.options(section):
                config_dict[section][option] = config_parser.get(section, option)
        return Config.from_dict(config_dict)

    @overrides(Persist)
    def to_str(self) -> str:
        config_parser = configparser.ConfigParser()
        config_dict = self.as_dict()
        for section in config_dict:
            config_parser.add_section(section)
            section_dict = config_dict[section]
            for key in section_dict:
                config_parser.set(section, key, str(section_dict[key]))
        str_io = StringIO()
        config_parser.write(str_io)
        return str_io.getvalue()

    @staticmethod
    def from_dict(config_dict: OuterConfigType) -> "Config":
        config_dict = dict(config_dict)  # copy that we can modify
        config = Config()

        config.general = Config.General.from_dict(
            Config._check_section(config_dict, "General")
        )
        config.lftp = Config.Lftp.from_dict(Config._check_section(config_dict, "Lftp"))
        config.controller = Config.Controller.from_dict(
            Config._check_section(config_dict, "Controller")
        )
        config.web = Config.Web.from_dict(Config._check_section(config_dict, "Web"))
        config.autoqueue = Config.AutoQueue.from_dict(
            Config._check_section(config_dict, "AutoQueue")
        )

        Config._check_empty_outer_dict(config_dict)
        return config

    def as_dict(self) -> OuterConfigType:
        # We convert all values back to strings
        # Use an ordered dict to main section order
        config_dict = collections.OrderedDict()
        config_dict["General"] = self.general.as_dict()
        config_dict["Lftp"] = self.lftp.as_dict()
        config_dict["Controller"] = self.controller.as_dict()
        config_dict["Web"] = self.web.as_dict()
        config_dict["AutoQueue"] = self.autoqueue.as_dict()
        return config_dict

    def has_section(self, name: str) -> bool:
        """
        Returns true if the given section exists, false otherwise
        :param name:
        :return:
        """
        try:
            return isinstance(getattr(self, name), InnerConfig)
        except AttributeError:
            return False
