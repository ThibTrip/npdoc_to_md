# +
import inspect
import warnings
from dataclasses import dataclass, field as dataclassfield
from typing import Any, ClassVar, Dict, List, Tuple, Union
from numpydoc.docscrape import ClassDoc, FunctionDoc, NumpyDocString

# local imports
from npdoc_to_md.helpers import previous_current_next


# -

# # Helpers

@dataclass(frozen=True)
class SectionsFinder:
    '''
    Gets all numpydoc style sections in a Python object's docstring
    **including custom defined sections** (numpydoc ignores them :/)
    and in order

    Attributes
    ----------
    sections_without_headers
        Sections of numpydoc for which there is no header e.g. "Signature"
        This is not used in this class by it is used by other modules
    standard_section_names
        Standard sections of numpydoc
    doc
        Object from numpydoc representing a parsed docstring
    docstring_cleaned
        Docstring cleaned with inspect.cleandoc

    Examples
    --------
    >>> def foo(a:int):
    ...     """
    ...     A dummy function
    ...
    ...     Parameters
    ...     ----------
    ...     a
    ...         Some number
    ...
    ...     My custom section
    ...     -----------------
    ...     It works!
    ...     """
    ...     pass
    >>>
    >>> sf = SectionsFinder(foo, ignore_custom_section_warning=True)
    >>> print(sf.all_visible_sections_start_indices)
    {'Parameters': 2, 'My custom section': 7}

    >>> print(sf.all_visible_sections_ranges)
    {'Parameters': range(4, 6), 'My custom section': range(9, 9)}

    >>> print(sf.custom_sections)
    {'My custom section': ['It works!']}

    >>> # note: I don't use pprint because in Python 3.7 we cannot avoid dict sorting
    >>> for k, v in sf.all_sections.items():
    ...     print(f'{k}={repr(v)}')
    Signature=''
    Summary=['A dummy function']
    Extended Summary=[]
    Parameters=[Parameter(name='a', type='', desc=['Some number'])]
    My custom section=['It works!']
    Returns=[]
    Yields=[]
    Receives=[]
    Raises=[]
    Warns=[]
    Other Parameters=[]
    Attributes=[]
    Methods=[]
    See Also=[]
    Notes=[]
    Warnings=[]
    References=''
    Examples=''
    '''
    py_obj:Any
    ignore_custom_section_warning:bool = dataclassfield(default=False, repr=False)
    sections_without_headers:ClassVar[Tuple[str]] = ('Signature', 'Summary', 'Extended Summary')
    # get a list of standard sections
    # note that "index" is not a section but a method listed under NumpyDocString.sections
    standard_section_names:ClassVar[Tuple[str]] = tuple([k for k in NumpyDocString.sections if k != 'index'])
    doc:Union[ClassDoc, FunctionDoc, NumpyDocString] = dataclassfield(init=False)
    docstring_cleaned:str = dataclassfield(init=False)

    def __post_init__(self):

        # pyobj must be a class, function or anything else that has a docstring...
        py_obj = self.py_obj
        if self.ignore_custom_section_warning:
            with warnings.catch_warnings():
                warnings.filterwarnings(action='ignore', category=UserWarning, message='Unknown section')
                doc = self._get_numpydoc_obj(py_obj)
        else:
            doc = self._get_numpydoc_obj(py_obj)

        # clean the docstring, handle the case when there is no docstring (__doc__ is None)
        docstring = py_obj.__doc__
        docstring_cleaned = inspect.cleandoc(docstring) if docstring is not None else ''

        # because we are in a frozen dataclass we need this workaround to set attributes
        object.__setattr__(self, 'doc', doc)
        object.__setattr__(self, 'docstring_cleaned', docstring_cleaned)

    @staticmethod
    def _get_numpydoc_obj(py_obj:Any):
        # special case where __doc__ is None e.g. with non overwritten dunder methods
        # such as "__dict__"
        if hasattr(py_obj, '__doc__') and getattr(py_obj, '__doc__') is None:
            return NumpyDocString('')

        # "normal" cases
        if inspect.isclass(py_obj):
            doc = ClassDoc(py_obj)
        elif inspect.isfunction(py_obj) or inspect.ismethod(py_obj):
            doc = FunctionDoc(py_obj)
        elif hasattr(py_obj, '__doc__'):
            doc = NumpyDocString(py_obj.__doc__)
        else:  # pragma: no cover
            raise TypeError(f'The object {py_obj} is not a class, function, method '
                            'or any other Python object that has a __doc__ attribute')
        return doc

    @property
    def docstring_lines(self):
        return self.docstring_cleaned.splitlines()

    @staticmethod
    def _find_from_lines(line:str, next_line:Union[str, None]) -> Union[str, None]:
        """
        Finds a section in numpydoc style docstring using a given line and the next one
        (or None if it is the last line in the docstring).

        If the line does not seem to correspond to a section, we return None.

        Examples
        --------
        >>> l1 = 'My Section'
        >>> l2 = '----------'
        >>> SectionsFinder._find_from_lines(line=l1, next_line=l2)
        'My Section'
        """
        # skip empty lines
        if next_line is None:  # last line -> cannot be a section
            return None
        if not len(line.strip()) or not len(next_line.strip()):
            return None

        # do an rstrip, we still need leading spaces on the left
        # to handle cases where the section separator is misaligned
        line, next_line = line.rstrip(), next_line.rstrip()

        # check if first letter is uppercase (otherwise we consider that's not a section)
        if not line.strip()[0].isupper():
            return None

        # if the length is not the same, then there is necessarily a misalignement
        # because we did a rstrip before
        # (and thus no section would be detected by numpydoc and we imitate this behavior)
        if len(line) != len(next_line):
            return None
        nb_chars = len(line)

        # go through previous and current line characters to determine if it's a section
        # note that we do need this complex code because like numpydoc we should
        # be able to parse sections that have leading spaces even after using cleandoc()
        # on the docstring
        header_reached = False
        section_name_chars = []
        for ix, (pc, c) in enumerate(zip(line.rstrip(), next_line.rstrip())):
            # check if we reached the header
            if not header_reached:
                header_reached = pc != ' '

            # until we reach the header we expect to have spaces on both lines
            if not header_reached:
                if not (pc == c == ' '):
                    return None
            else:
                section_name_chars.append(pc)
                if c not in ('-', '='):
                    return None

            # if the for loop went through all characters without breaking
            # it means we found a section
            if ix == (nb_chars - 1):
                return ''.join(section_name_chars)

    @property
    def all_visible_sections_start_indices(self) -> Dict[int, str]:
        """
        Returns a dictionary of visible section names and where they
        start (see class Examples)
        """
        sections = {}
        lines = self.docstring_lines
        # case of empty docstring
        if not len(lines):
            return {}
        # normal case
        for ix, (_, line, next_line) in enumerate(previous_current_next(lines)):
            section_name:Union[str, None] = self._find_from_lines(line=line, next_line=next_line)
            if section_name is not None:
                sections[section_name] = ix
        return sections

    @property
    def all_visible_sections_ranges(self) -> Dict[str, range]:
        """
        Returns a dictionary of visible section names and their span
        (see class Examples)
        """
        # Example for the values of variables below:
        # start_indices = {5:'Parameters', 10:'Examples'}
        # shifted = [10, 25]
        # ranges = [range(5, 9), range(10, 25)]
        # return {'Parameters':range(5, 9), 'Examples':range(10, 25)}
        sections_indices = self.all_visible_sections_start_indices
        if not len(sections_indices):
            return {}
        shifted = list(sections_indices.values())[1:] + [len(self.docstring_lines)]
        assert len(sections_indices) == len(shifted)
        # start + 2 because we need to remove the header and the separator line
        ranges = [range(a + 2, b - 1) for a, b in zip(sections_indices.values(), shifted)]
        return {v:r for r, v in zip(ranges, sections_indices.keys())}

    @property
    def all_visible_sections(self) -> List[str]:
        """
        Returns a list of all visible sections
        """
        return list(self.all_visible_sections_ranges)

    @property
    def custom_sections(self) -> Dict[str, List[str]]:
        """
        Returns a dict of custom sections and their content (see class Examples)
        """
        sections = {}
        for section, range_ in self.all_visible_sections_ranges.items():
            if section not in self.standard_section_names:
                lines = self.docstring_lines[range_.start:range_.stop + 1]
                sections[section] = lines
        return sections

    @property
    def standard_sections(self) -> Dict[str, list]:
        """
        Returns a dictionary similar to NumpyDocString(obj).sections
        """
        return {k:self.doc[k] for k in self.standard_section_names}

    @property
    def all_sections(self) -> Dict[str, list]:
        """
        Returns a dictionary with standard sections from numpydoc AND
        custom sections we found (see class Examples)
        """
        # we need to iterate through all sections to preserve the docstring order
        # instead of just adding properties custom_sections and sections
        standard_sections = self.standard_sections
        custom_sections = self.custom_sections
        all_visible_sections = self.all_visible_sections

        # case when custom sections cannot be positionned relative to standard
        # ones because there are no visible standard sections
        # in this case we'll put custom sections after "Extended Summary"
        only_custom = all(v in custom_sections for v in all_visible_sections)
        if only_custom:
            default_keys = list(standard_sections.keys())
            default_values = list(standard_sections.values())
            ix_custom = default_keys.index('Extended Summary') + 1

            keys = default_keys[0:ix_custom] + list(custom_sections.keys()) + default_keys[ix_custom:]
            values = default_values[0:ix_custom] + list(custom_sections.values()) + default_values[ix_custom:]
            return dict(zip(keys, values))

        # case when custom sections can be positionned relative to standard ones
        # local helper
        def get_consecutive_custom_section(section_name:str) -> Union[None, List[str]]:
            if section_name in all_visible_sections:
                ix = all_visible_sections.index(section_name) + 1
                subset = all_visible_sections[ix:]
                return next((k for k in subset if k in custom_sections), None)
            else:
                return None

        # get all sections in order
        all_sections = {}
        for k, v in standard_sections.items():
            all_sections[k] = v
            # check if a custom section follows the standard section
            consecutive_custom_section = get_consecutive_custom_section(k)
            if consecutive_custom_section is not None:
                v_custom = custom_sections[consecutive_custom_section]
                all_sections[consecutive_custom_section] = v_custom
        return all_sections

    def __getitem__(self, key:str):
        # that's not particulary efficient since the property
        # will be computed each time but it's not a big deal
        return self.all_sections[key]
