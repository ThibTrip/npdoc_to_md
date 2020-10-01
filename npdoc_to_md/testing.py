"""
Example of quite useless functions to test parsing of docstrings.
"""


# # Functions

# ## First example
#
# Contains most sections from a numpy docstring (see https://numpydoc.readthedocs.io/en/latest/format.html)

def example_func(a:int, b:int, useless_param=None) -> int:
    """
    Example function that sums to integers.

    Some extended summary.

    Notes
    -----
    Some notes.
    More notes.

    Warnings
    --------
    Cautionnary notes for the user.
    More warning notes.

    References
    ----------
    [0] Me

    See Also
    --------
    example_func2, example_func3
        Other useless functions.
        Multiline test.

    Parameters
    ----------
    a : int
        First number.
        Multiline test.
    b : int

    Other Parameters
    ----------------
    useless_param : None
        Some useless parameter.
        Multiline test.

    Examples
    --------
    * fist example
    >>> example_func(1, 1)
    2

    * second example
    {{python}}
    >>> example_func(2, 2)
    4

    * third example (test markdown)
    {{markdown}}
    >>> import pandas as pd
    >>> df = pd.DataFrame({'A':[1, 2]})
    >>> print(df.to_markdown())
    |    |   A |
    |---:|----:|
    |  0 |   1 |
    |  1 |   2 |

    * fourth example (raw code block)
    {{raw}}
    >>> print('Hello world!')
    Hello world!

    Returns
    -------
    c : int
        Result of a + b.
        Multiline test.

    Raises
    ------
    TypeError
        If a or b is not a number.

    Warns
    -----
    UserWarning
        Never (this is just an example)
    """
    if any(not (isinstance(x, int)) for x in (a, b)):
        raise TypeError('a and b must be integers')
    c = a + b
    return c


# ## Second example
#
# For generators.

def example_func2(nb_vals=10):
    """
    Generator example (for testing the parsing of Yields and Receives sections).

    Receives
    --------
    nb_vals : int, default 10
        Number of values to yield.

    Yields
    ------
    i : int
        Incrementing integers.
    """
    for i in range(10):
        yield i


# ## Third example
#
# For See Also section in example_func (a valid function is required)

def example_func3():
    """
    Dummy function for testing See Also section in example_func.
    """
    pass


# # Fourth example
#
# With a blankline in the examples

def example_func4():
    """
    Function to test if we can successfully remove doctest blanklines.
    See https://docs.python.org/3.8/library/doctest.html#how-are-docstring-examples-recognized

    Examples
    --------
    >>> example_func4()
    <BLANKLINE>
    foo
    """
    print('')
    print('foo')


# # Classes

class ExampleClass():
    """
    Class example.

    Extended summary.

    Attributes
    ----------
    first_name : str
        Some first name
        Extended description
    last_name : str
        Some last name

    Examples
    --------
    >>> ex = ExampleClass('john', 'doe')
    """
    def __init__(self, first_name:str, last_name:str):
        self.first_name = first_name
        self.last_name = last_name


    def example_method(self):
        """
        Test for methods.
        
        Extended summary.

        Examples
        --------
        >>> ex = ExampleClass('john', 'doe')
        >>> ex.example_method()
        john
        """
        print(self.first_name)
        
        
    @staticmethod
    def test_static_method():
        """
        Test static method...

        Examples
        --------
        >>> ex = ExampleClass('john', 'doe')
        >>> ex.test_static_method()
        """
        pass


    @classmethod
    def test_class_method(cls):
        """
        Test class method...

        Examples
        --------
        >>> ExampleClass.test_class_method()
        """
        pass
