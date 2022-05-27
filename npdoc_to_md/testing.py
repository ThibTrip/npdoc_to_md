"""
Dummy objects (classes, functions, ...) for demos of the library and tests

Notes
-----
The docstring of this module will be used for docstring rendering tests in pytest.
Which is why I am also going to include some examples here and a custom section
"Functions".

Examples
--------
>>> from npdoc_to_md.testing import DocumentedClassExample
>>>
>>> ex = DocumentedClassExample(first_name='John', last_name='Doe')
>>> ex.full_name
'John Doe'

Functions
---------
* create_random_table
  Returns a random table (pandas DataFrame)
* now_utc
  Returns the current date and time in UTC
* ...
"""
import datetime
from dataclasses import dataclass, fields as dataclassfields
from numpydoc.docscrape import NumpyDocString
from typing import Dict, List, Optional, Union


# # Dummy objects

# +
def create_random_table(nb_rows:int=5, seed:Optional[int]=None) -> 'pandas.DataFrame':
    """
    Returns a random table (pandas DataFrame). You must
    have pandas (and numpy which comes with it) installed!

    Parameters
    ----------
    nb_rows
        How many rows to generate
    seed
        Any number for having predictable outputs

    Examples
    --------
    >>> df = create_random_table(seed=0)
    >>> print(df.to_markdown(index=False))
    |   A |   B |   C |   D |
    |----:|----:|----:|----:|
    |  44 |  47 |  64 |  67 |
    |  67 |   9 |  83 |  21 |
    |  36 |  87 |  70 |  88 |
    |  88 |  12 |  58 |  65 |
    |  39 |  87 |  46 |  88 |
    """
    try:
        import pandas as pd
        import numpy as np
    except (ModuleNotFoundError, ImportError) as e:  # pragma: no cover
        raise ModuleNotFoundError('You need to install the optional dependency pandas for this '
                                  'test function (pip install pandas)') from e

    if seed is not None:
        np.random.seed(seed)
    return pd.DataFrame(np.random.randint(0, 100, size=(nb_rows, 4)),
                        columns=list('ABCD'))


def now_utc() -> datetime.datetime:
    """
    Returns the current date and time in UTC

    Examples
    --------
    >>> current_dt_utc = now_utc()
    >>> current_dt_utc  # doctest: +SKIP
    datetime.datetime(2022, 4, 14, 19, 46, 6, 504371, tzinfo=datetime.timezone.utc)
    """
    return datetime.datetime.now().astimezone(datetime.timezone.utc)


# -

# ## Functions and classes with empty docstrings/signatures/sections
#
# To try to break the library

# +
def empty_function():
    pass  # pragma: no cover


class EmptyClass:
    pass  # pragma: no cover


# make a function and a class with empty sections in the docstrings
# note that we necessarily need a line break between sections
# otherwise numpydoc will think everything belongs to the
# first section
def make_docstring_with_empty_sections():
    invisible_sections = ('Signature', 'Summary', 'Extended Summary')
    # since we cannot have both Yields and Returns we will remove Returns
    # also "index" is not a section but a method listed under NumpyDocString.sections
    irrelevant_sections = ('index', 'Returns')
    lines = []
    for section in NumpyDocString.sections:
        if section in invisible_sections + irrelevant_sections:
            continue
        lines.extend([section, '-' * len(section), ''])
    return '\n'.join(lines)


def empty_doc_sections_function():
    pass  # pragma: no cover


class EmptyDocSectionsClass:
    pass  # pragma: no cover


empty_doc_sections_function.__doc__ = make_docstring_with_empty_sections()
EmptyDocSectionsClass.__doc__ = make_docstring_with_empty_sections()


# -

# # Example of fully documented objects

# ## Functions

# +
def documented_func_example(a:int, b:int, *,
                            # add a bunch of stupid kwargs to try to break the library
                            # especially the escaping of special characters
                            useless_param=None,
                            _bad_name_param1=None,
                            __bad_name_param2=None,
                            # note: do not try Optional[str] as this gets converted to Union[str, None]
                            # in Python 3.7
                            crazy_typing_param:Union[Dict[str, int], List[str]]=None,
                            **kwargs) -> int:
    r"""
    Example function that sums to integers. This function is used for pytest.
    It does not really make sense, this is just for testing docstring rendering.

    Some extended summary.

    Multiline test.

    Custom Section
    --------------
    This is for testing that custom sections are not ignored (as opposed to what
    numpydoc does) and we can fetch the content in the right order.

    Multiline test.

    Notes
    -----
    Some notes.

    Multiline test.

    Warnings
    --------
    Cautionnary notes for the user.
    More warning notes.

    Multiline test.

    References
    ----------
    [0] Me

    Multiline test.

    See Also
    --------
    empty_function, EmptyClass, empty_doc_sections_function, EmptyDocSectionsClass
        Other useless functions.

        Numpydoc deletes line breaks for section "See Also" so no multiline test here...
        The next function I put in this section will have no description.
    now_utc

    Parameters
    ----------
    a : int
        First number.

        Multiline test.
    b : int

    Other Parameters
    ----------------
    useless_param
        Some useless parameter.

        Multiline test.

    _bad_name_param1
    __bad_name_param2
    crazy_typing_param
        Parameter with complex typing
    optional_type_param
        Parameter with optional typing

    Examples
    --------
    We are going to try to break our library by:
    1. Putting text before examples or not
    2. Separating examples by line breaks (also with irrelevant leading spaces) or not

    We'll then check if the library still manages to separate examples properly

    * example 1
    {{python}}
    >>> documented_func_example(1, 1)
    2

    * example 2
    {{python}}
    >>> documented_func_example(2, 2)
    4

    ---

    #### Examples unrelated to the function

    * test rendered markdown
    {{markdown_rendered}}
    >>> import pandas as pd
    >>> df = pd.DataFrame({'A':[1, 2]})
    >>> print(df.to_markdown())
    |    |   A |
    |---:|----:|
    |  0 |   1 |
    |  1 |   2 |
    
    * test raw code block
    {{raw}}
    >>> print('Hello world!')
    Hello world!

    * test non rendered markdown
    {{markdown}}
    >>> print('# some markdown string\n* test')
    # some markdown string
    * test

    >>> print('test')
    test
    >>> print('foo\n')
    foo
    <BLANKLINE>

    Returns
    -------
    c : int
        Result of a + b.

        Multiline test.

    Raises
    ------
    TypeError
        If a or b is not a number.

        Multiline test.

    Warns
    -----
    UserWarning
        Never occurs (this is just an example)

        Multiline test.
    """
    return a + b


def documented_generator_func_example(nb_vals=10):
    """
    Generator example (for testing the parsing of Yields and Receives sections).
    Simply yields a range from 0 to `nb_vals`.

    Receives
    --------
    nb_vals : int, default 10
        Number of values to yield.

        Multiline test.

    Yields
    ------
    i : int
        Incrementing integers.

        Multiline test.

    Examples
    --------
    >>> for i in documented_generator_func_example(2):
    ...    print(i)
    0
    1
    """
    for i in range(nb_vals):
        yield i


# -

# ## Classes

@dataclass(frozen=True)
class DocumentedClassExample:
    """
    Example dataclass representing a person. This class is used for pytest.
    It does not really make sense, this is just for testing docstring rendering.

    Attributes
    ----------
    full_name : str
        first name + last name (both names in title case and separated by a space).

        Multiline test.

    Examples
    --------
    >>> ex = DocumentedClassExample(first_name='John', last_name='Doe')
    >>> ex.full_name
    'John Doe'
    """
    first_name:str
    last_name:str

    @property
    def full_name(self) -> str:
        """
        Returns the full name using the names part defined in the instance.
        This is a test for rendering docstrings of properties.

        Returns
        -------
        str
            Full name

        Examples
        --------
        >>> ex = DocumentedClassExample(first_name='john', last_name='doe')
        >>> ex.full_name
        'John Doe'
        """
        return f'{self.first_name.title()} {self.last_name.title()}'

    def example_method(self) -> None:
        """
        Prints the first name defined in the instance.
        This is a test for rendering docstrings of methods.

        Examples
        --------
        >>> d = DocumentedClassExample('John', 'Doe')
        >>> d.example_method()
        John
        """
        print(self.first_name)

    @staticmethod
    def example_static_method() -> List[str]:
        """
        Prints the names of the dataclass fields.
        This is a test for rendering docstrings of staticmethods.

        Examples
        --------
        >>> DocumentedClassExample.example_static_method()
        ['first_name', 'last_name']

        >>> d = DocumentedClassExample('John', 'Doe')
        >>> d.example_static_method()
        ['first_name', 'last_name']
        """
        fields = dataclassfields(DocumentedClassExample)
        return [f.name for f in fields]

    @classmethod
    def test_class_method(cls) -> 'DocumentedClassExample':
        """
        Returns a "John Doe" instance of the class.
        This is a test for rendering docstrings of class methods.

        Examples
        --------
        >>> DocumentedClassExample.test_class_method()
        DocumentedClassExample(first_name='John', last_name='Doe')
        """
        return cls(first_name='John', last_name='Doe')

    def _example_private_method(self) -> None:
        """
        Some private method
        """
        pass  # pragma: no cover
