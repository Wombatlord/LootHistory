"""
This module is intended to create a lightweight way to specify the command line arguments
that are expected, parse them and allow them to be accessed in code.
"""
from __future__ import annotations

import sys
from collections import namedtuple
from typing import List, Any, Tuple, Optional, Set, Dict, Mapping, Union


class ShortName(str):
    def __new__(cls, short_name_str: str):
        if not len(short_name_str) == 1:
            raise ValueError(f"Short names must be a single character, {short_name_str} supplied")

        return super(ShortName, cls).__new__(cls, short_name_str)


class FlagSpec(namedtuple("FlagNames", ["short_name", "long_name"])):
    def __new__(cls, short_name: str, long_name: str) -> FlagSpec:
        short_name = ShortName(short_name)
        return super(FlagSpec, cls).__new__(cls, (short_name, long_name))


class OptionSpec(namedtuple("FlagNames", ["short_name", "long_name", "value_type", "default"])):
    def __new__(cls, short_name: str, long_name: str, value_type: type, default: Optional = None) -> OptionSpec:
        short_name = ShortName(short_name)
        if not value_type(default) is not default:
            raise TypeError("The default value must have the type specified by value_type")
        return super(OptionSpec, cls).__new__(cls, (short_name, long_name, value_type, default))


class PositionalArgSpec(namedtuple("FlagNames", ["name", "value_type"])):
    def __new__(cls, name: str, value_type: type) -> PositionalArgSpec:
        return super(PositionalArgSpec, cls).__new__(cls, (name, value_type))


class NameConflict(ValueError):
    @classmethod
    def arg_name_conflict(cls, name: str) -> NameConflict:
        msg = f"Another positional argument is using the name provided ({name})"
        return cls(msg)

    @classmethod
    def short_name_conflict(cls, name: str) -> NameConflict:
        msg = f"Another part of the arg spec is using the short name provided ({name})"
        return cls(msg)

    @classmethod
    def long_name_conflict(cls, name: str) -> NameConflict:
        msg = f"Another part of the arg spec is using the long name provided ({name})"
        return cls(msg)


class ArgSpec:
    def __init__(self):
        self._flags: Set[FlagSpec] = set()
        self._options: Set[OptionSpec] = set()
        self._args: List[PositionalArgSpec] = []
        self._short_names: Set[str] = set()
        self._long_names: Set[str] = set()
        self._arg_names: Set[str] = set()
        self._parse_errors: List[str] = []

    def _validated(self, named_segment: Union[FlagSpec, OptionSpec, PositionalArgSpec]) -> ArgSpec:
        if isinstance(named_segment, (FlagSpec, OptionSpec)):
            if named_segment.short_name in self._short_names:
                raise NameConflict.short_name_conflict(named_segment.short_name)
            if named_segment.long_name:
                raise NameConflict.long_name_conflict(named_segment.long_name)

            self._short_names.add(named_segment.short_name)
            self._short_names.add(named_segment.long_name)

        if isinstance(named_segment, PositionalArgSpec):
            if named_segment.name in self._arg_names:
                raise NameConflict.arg_name_conflict(named_segment.name)

            self._arg_names.add(named_segment.name)

        return self

    @property
    def named_args(self) -> Dict[str, OptionSpec]:
        named_args = {option.long_name: option for option in self._options | self._flags}
        named_args = {**named_args, **{option.short_name: option for option in self._options | self._flags}}
        return named_args

    def get_named_arg(self, name) -> OptionSpec:
        return self.named_args.get(name)

    def define_flag(self, short_name: str, long_name: str) -> ArgSpec:
        spec = FlagSpec(short_name, long_name)
        self._validated(spec)._flags.add(spec)
        return self

    def define_option(self, short_name: str, long_name: str, value_type: type, default: Optional = None) -> ArgSpec:
        spec = OptionSpec(short_name, long_name, value_type, default)
        self._validated(spec)._options.add(spec)
        return self

    def expect_arg(self, name: str, value_type: type) -> ArgSpec:
        spec = PositionalArgSpec(name, value_type)
        self._validated(spec)._args.append(spec)
        return self

    def extract_named_args(self, argv: List[str]) -> Tuple[List[str], Set[str], Mapping]:
        supplied_names = self.parse_supplied_names(argv)
        positional_args = [*argv]
        kwargs = {}
        flags = set()
        for name in supplied_names:
            named_arg_spec = self.get_named_arg(name)
            if not named_arg_spec:
                continue

            if isinstance(named_arg_spec, FlagSpec):
                flags.add(named_arg_spec.long_name)
                positional_args.remove(name)
                continue

            value_index = argv.index(f"-{name}") + 1
            if value_index >= len(argv) and isinstance(named_arg_spec, OptionSpec):
                kwargs[named_arg_spec.long_name] = named_arg_spec.default
                positional_args.remove(name)
                continue

            value = argv[value_index]
            if not value.startswith(("-", "--")):
                kwargs[named_arg_spec.long_name] = named_arg_spec.value_type(value)
                positional_args.remove(name)
                positional_args.remove(value)
            else:
                kwargs[named_arg_spec.long_name] = named_arg_spec.default
                positional_args.remove(name)

        positional_args = [self._args[i].value_type(positional_arg) for i, positional_arg in enumerate(positional_args)]

        return positional_args, flags, kwargs

    def parse_supplied_names(self, argv):
        supplied_names_short = [
            item for item in argv[1:]
            if f"-{item}" in self._short_names
        ]
        supplied_names = [
            *supplied_names_short,
            *[
                item for item in argv[1:]
                if f"--{item}" in self._long_names
            ]
        ]
        return supplied_names

    def partition(self, argv: List[str]) -> Tuple[List, Set, Mapping]:
        return self.extract_named_args(argv)


class ParsedArgs(namedtuple("Inputs", ["args", "flags", "named_args"])):
    args: List[Any]
    flags: Set[str]
    named_args: Dict[str, Any]

    @classmethod
    def parse(cls, arg_spec: ArgSpec, argv: Optional[List[str]] = None) -> ParsedArgs:
        return cls(*arg_spec.partition(argv))


def parse_argv(arg_spec: ArgSpec) -> ParsedArgs:
    return ParsedArgs.parse(arg_spec, sys.argv)
