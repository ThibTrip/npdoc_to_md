# +
"""
Configurations and helpers for test modules
"""
import inspect
import logging
import os
import tempfile
from dataclasses import dataclass, field as dataclassfield
from typing import Callable, List, Optional, Union

from npdoc_to_md.logger import log


# -

# # Helpers

# ## CLI Runner

@dataclass(frozen=True)
class CLIRunner:
    """
    Runs a Python function in the CLI (see `run` method).

    The attributes `mandatory`, `optionals` and `flags` (see below)
    are infered from `kwargs` (see Parameters) and the signature of `func`.

    Parameters
    ----------
    func
    kwargs
        All parameters you would pass to the function if it were
        in Python and all given as keywords arguments.
        This means that positional only parameters will not work.
    command
        Command corresponding to the `func` in the CLI
        or list of command + subcommand(s)
    hyphenize
        If True, converts underscores to hyphens
        (used for testing if those characters are
         interchangeable as expected in our CLI)

    Attributes
    ----------
    mandatory
        Mandatory arguments in the form of a dict
    optionals
        Optional arguments in the form of a dict
    flags
        CLI flags e.g. "--verbose"

    Examples
    --------
    >>> from npdoc_to_md.core import render_obj_docstring
    >>>
    >>> cli = CLIRunner(func=render_obj_docstring,
    ...                 command=['npdoc_to_md', 'render_obj_docstring'],
    ...                 kwargs=dict(obj='npdoc_to_md.testing.now_utc',
    ...                             alias="now_utc",
    ...                             examples_md_lang='raw',
    ...                             remove_doctest_skip=True,
    ...                             remove_doctest_blanklines=True,
    ...                             md_section_level=3),
    ...                 hyphenize=True)
    >>> cli
    CLIRunner(command=['npdoc-to-md', 'render-obj-docstring'], mandatory={'obj': 'npdoc_to_md.testing.now_utc'}, \
optionals={'alias': 'now_utc', 'examples-md-lang': 'raw', 'md-section-level': 3}, \
flags=['remove-doctest-blanklines', 'remove-doctest-skip'])
    """
    func:Callable = dataclassfield(repr=False)
    kwargs:dict = dataclassfield(repr=False)
    command:Union[str, List[str]]
    hyphenize:bool = dataclassfield(default=False, repr=False)
    mandatory:dict = dataclassfield(init=False)
    optionals:dict = dataclassfield(init=False)
    flags:List[str] = dataclassfield(init=False)

    def __post_init__(self):
        # verifications
        assert isinstance(self.command, (list, str))
        assert len(self.command) > 0

        # inspect parameters of `func`
        params:List[inspect.Parameter] = inspect.signature(self.func).parameters
        mandatory, optionals, flags = {}, {}, []
        for param in params.values():

            # handle non provide parameters
            # raise if mandatory param missing
            is_mandatory = param.default is inspect._empty
            if param.name not in self.kwargs:
                if is_mandatory:  # pragma: no cover
                    raise ValueError(f'Missing mandatory parameter {param.name}')
                continue

            # classify parameters
            if is_mandatory:
                mandatory[param.name] = self.kwargs[param.name]
            elif isinstance(param.default, bool):
                value = self.kwargs[param.name]
                if not isinstance(value, bool):
                    raise TypeError(f'Expected bool for parameter "{param.name}". Got type {type(value)}')
                # flags are only used to denote a True value
                if value is True:
                    flags.append(param.name)
            else:
                optionals[param.name] = self.kwargs[param.name]

        # convert underscores to hyphens
        if self.hyphenize:
            rename = lambda k: k.replace('_', '-')
            # rename command
            # note: most likely we will always provide commands
            # as a list (the library works with subcommands) so no need to cover this
            if isinstance(self.command, str):  # pragma: no cover
                command = rename(self.command)
            else:
                assert isinstance(self.command, list)
                command = [rename(c) for c in self.command]
            object.__setattr__(self, 'command', command)

            # rename params
            mandatory = {rename(k):v for k, v in mandatory.items()}
            optionals = {rename(k):v for k, v in optionals.items()}
            flags = [rename(v) for v in flags]

        object.__setattr__(self, 'mandatory', mandatory)
        object.__setattr__(self, 'optionals', optionals)
        object.__setattr__(self, 'flags', flags)

    def run(self, extras:Optional[List[str]]=None):
        """
        Runs our command in the CLI

        Parameters
        ----------
        extras
            Any extra arguments you want. They will be put at the end.
            This is useful for Python-fire if we want to access
            properties.
            E.g. "npdoc-to-md render-folder . - 0 - rendered_text"
            will give us the attribute "rendered_text" of the first rendered file
        """
        # get plumbum
        try:
            from plumbum import local
        except ModuleNotFoundError as e:  # pragma: no cover
            raise ModuleNotFoundError('Please install testing dependency `plumbum` (pip install plumbum)') from e

        # get command
        commands = [self.command] if isinstance(self.command, str) else self.command
        command, args = commands[0], commands[1:]
        runner = local[command]

        # get params
        extras = [] if extras is None else extras
        for k, v in self.mandatory.items():
            args.append(f'-{k}')
            args.append(v)
        for k, v in self.optionals.items():
            args.append(f'--{k}')
            args.append(v)
        args.extend([f'--{f}' for f in self.flags])
        args.extend([e.replace('_', '-') if self.hyphenize else e for e in extras])

        log(f'Running command {command} with args: {args}', level=logging.INFO)

        return runner.__getitem__(args)()  # cannot do something like runner[*args]()


# ## Temporary files

class CustomNamedTemporaryFile:
    """
    This custom implementation is needed because of the following limitation of tempfile.NamedTemporaryFile:

    > Whether the name can be used to open the file a second time, while the named temporary file is still open,
    > varies across platforms (it can be so used on Unix; it cannot on Windows NT or later).

    See https://stackoverflow.com/a/63173312
    """

    def __init__(self, mode='wb', delete=True):
        self._mode = mode
        self._delete = delete

    def __enter__(self):
        # Generate a random temporary file name
        file_name = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        # Ensure the file is created
        open(file_name, "x").close()
        # Open the file in the given mode
        self.file = open(file_name, self._mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        if self._delete:
            os.remove(self.file.name)
