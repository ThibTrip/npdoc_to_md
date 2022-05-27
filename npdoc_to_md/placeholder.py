# +
"""
Tools for finding and parsing placeholders described in the wiki of the library
"""
import json
import logging
from dataclasses import dataclass, field as dataclass_field
from typing import ClassVar, Tuple

# local imports
from npdoc_to_md.config import Config
from npdoc_to_md.logger import log


# -

# # Placeholder class

@dataclass
class Placeholder:
    """
    Helper for finding placeholders defined by this library in strings or markdown files.

    Attributes
    ----------
    required
        Mandatory parameters for placeholders
    optional
        Optional parameters for placeholders

    Examples
    --------
    >>> lines = ['Pandas is a cool library. Here is for instance the DataFrame object:',
    ...          '{{"obj":"pandas.DataFrame", "alias":"pd.DataFrame", "remove_doctest_blanklines":true}}']
    >>>
    >>> for line in lines:
    ...     placeholder = Placeholder.search(line)
    ...     if placeholder:
    ...         print(placeholder.obj_namespace, placeholder.config, sep=' | ')
    pandas.DataFrame | Config(alias='pd.DataFrame', examples_md_lang='python', remove_doctest_blanklines=True, \
remove_doctest_skip=False, md_section_level=3, ignore_custom_section_warning=False, members=[])
    """
    line:str
    parsed:dict = dataclass_field(init=False)
    obj_namespace:str = dataclass_field(init=False)
    config:Config = dataclass_field(init=False)
    required:ClassVar[Tuple[str]] = ('obj',)
    optional:ClassVar[Tuple[str]] = tuple(Config.__dataclass_fields__.keys())

    def __post_init__(self):
        line = self.line
        parsed:dict = json.loads(line[1:-1])

        # validate
        # 1) mandatory keys
        missing_required = [k for k in self.required if k not in parsed]
        if missing_required:
            raise ValueError(f'The mandatory keys {missing_required} are missing from a placeholder. '
                             f'The faulty line was:\n{line}')

        # 2) extra keys (not allowed)
        all_keys = list(self.required) + list(self.optional)
        extra_keys = [k for k in parsed if k not in all_keys]
        if extra_keys:
            raise ValueError(f'Unexpected keys {extra_keys} in a placeholder of numpydoc_to_md. '
                             f'Allowed keys are: {all_keys}. Faulty line:\n{line}')

        # create config object (which will validate it as well)
        obj_namespace = parsed['obj']  # don't pop "obj" we need it for attribute `parsed`
        kwargs = {k:v for k, v in parsed.items() if k != 'obj'}
        config = Config(**kwargs)

        # because we are in a frozen dataclass we need this workaround to set attributes
        object.__setattr__(self, 'parsed', parsed)
        object.__setattr__(self, 'obj_namespace', obj_namespace)
        object.__setattr__(self, 'config', config)

    @classmethod
    def search(cls, line:str) -> 'Placeholder':
        """
        If given line looks like a placeholder for our library (starts with "{{" and ends
        with "}}") we attempt to parse it (this may raise various exceptions) and return an instance
        of the class.
        Otherwise we return None.
        """
        line = line.strip()
        return cls(line=line) if line.startswith('{{') and line.endswith('}}') else None

    @classmethod
    def search_no_err(cls, line:str) -> 'Placeholder':
        """
        Same as method `search` (see its docstring) but when an exception occurs:
        * it is logged and not raised
        * None is returned

        Examples
        --------
        >>> line = '{{"obj":"datetime.datetime"}}'
        >>> placeholder = Placeholder.search_no_err(line=line)
        >>> print(placeholder.parsed)
        {'obj': 'datetime.datetime'}

        >>> # fails due to extra key
        >>> line = '{{"obj":"datetime.datetime", "invalid_key":"foo"}}'
        >>> placeholder = Placeholder.search_no_err(line=line)
        >>> print(placeholder)
        None

        >>> # fails due to missing mandatory "obj" key
        >>> line = '{{"not a placeholder":"foo"}}'
        >>> placeholder = Placeholder.search_no_err(line=line)
        >>> print(placeholder)
        None
        """
        line = line.strip()
        # case where it is definitely not a placeholder
        if not (line.startswith('{{') and line.endswith('}}')):
            return None
        # try to parse the placeholder
        try:
            return cls(line=line)
        except Exception:
            log(f'An exception occured when rendering this placeholder: {line}',
                level=logging.ERROR, exc_info=True)
            return None
