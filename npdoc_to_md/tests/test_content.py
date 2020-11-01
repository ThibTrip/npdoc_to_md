# +
from npdoc_to_md.testing import (example_func,
                                 example_func2,
                                 example_func3,
                                 example_func4,
                                 ExampleClass)

from npdoc_to_md import render_md_from_obj_docstring, render_md_string
import pytest
# -

# # Expectations

# +
expected_md1 = """**<span style="color:purple">example&#95;func</span>_(a: int, b: int, useless_param=None) -> int_**


Example function that sums to integers.


Some extended summary.

#### Parameters
* a : <b><i>int</i></b>  First number.
	Multiline test.
* b : <b><i>int</i></b> 

#### Returns
* c : <b><i>int</i></b>  Result of a + b.
	Multiline test.

#### Raises
<b><i>TypeError</i></b>  If a or b is not a number.

#### Warns
<b><i>UserWarning</i></b>  Never (this is just an example)

#### Other Parameters
* useless_param : <b><i>None</i></b>  Some useless parameter.
	Multiline test.

#### See Also
* example_func2, example_func3 : Other useless functions.
Multiline test.

#### Notes
Some notes.
More notes.

#### Warnings
Cautionnary notes for the user.
More warning notes.

#### References
[0] Me

#### Examples
* fist example
```python
example_func(1, 1)
```
```python
2
```

* second example
```python
example_func(2, 2)
```
```python
4
```

* third example (test markdown)
```python
import pandas as pd
df = pd.DataFrame({'A':[1, 2]})
print(df.to_markdown())
```
|    |   A |
|---:|----:|
|  0 |   1 |
|  1 |   2 |

* fourth example (raw code block)
```python
print('Hello world!')
```
```
Hello world!
```"""

expected_md2 = """**<span style="color:purple">example&#95;func2</span>_(nb_vals=10)_**


Generator example (for testing the parsing of Yields and Receives sections).


#### Yields
* i : <b><i>int</i></b>  Incrementing integers.

#### Receives
* nb_vals : <b><i>int, default 10</i></b>  Number of values to yield."""

expected_md3 = """**<span style="color:purple">example&#95;func3</span>_()_**


Dummy function for testing See Also section in example_func."""

expected_md4 = """**<span style="color:purple">ExampleClass</span>_(first_name: str, last_name: str)_**


Class example.


Extended summary.

#### Attributes
* first_name : <b><i>str</i></b>  Some first name
	Extended description
* last_name : <b><i>str</i></b>  Some last name

#### Examples
```python
ex = ExampleClass('john', 'doe')
```"""


# -

# # Test rendering from object docstring

@pytest.mark.parametrize("func, func_name, expected_md", [(example_func, 'example_func', expected_md1),
                                                          (example_func2, 'example_func2', expected_md2),
                                                          (example_func3, 'example_func3', expected_md3),
                                                          (ExampleClass, 'ExampleClass', expected_md4)])
def test_rendering_from_object_docstring(func, func_name, expected_md):
    md = render_md_from_obj_docstring(func, func_name)
    assert md == expected_md


# # Test rendering from markdown string

# +
expected_md_string_rendered = """Wow such nice function!

# Test docstring

**<span style="color:purple">npdoc&#95;to&#95;md.testing.example&#95;func</span>_(a: int, b: int, useless_param=None) -> int_**


Example function that sums to integers.


Some extended summary.

#### Parameters
* a : <b><i>int</i></b>  First number.
	Multiline test.
* b : <b><i>int</i></b> 

#### Returns
* c : <b><i>int</i></b>  Result of a + b.
	Multiline test.

#### Raises
<b><i>TypeError</i></b>  If a or b is not a number.

#### Warns
<b><i>UserWarning</i></b>  Never (this is just an example)

#### Other Parameters
* useless_param : <b><i>None</i></b>  Some useless parameter.
	Multiline test.

#### See Also
* example_func2, example_func3 : Other useless functions.
Multiline test.

#### Notes
Some notes.
More notes.

#### Warnings
Cautionnary notes for the user.
More warning notes.

#### References
[0] Me

#### Examples
* fist example
```python
example_func(1, 1)
```
2

* second example
```python
example_func(2, 2)
```
```python
4
```

* third example (test markdown)
```python
import pandas as pd
df = pd.DataFrame({'A':[1, 2]})
print(df.to_markdown())
```
|    |   A |
|---:|----:|
|  0 |   1 |
|  1 |   2 |

* fourth example (raw code block)
```python
print('Hello world!')
```
```
Hello world!
```"""

def test_rendering_from_markdown_string():
    md = """Wow such nice function!\n\n# Test docstring\n\n{{"obj":"npdoc_to_md.testing.example_func", "ex_md_flavor":"markdown"}}"""
    rendered = render_md_string(md)
    assert rendered == expected_md_string_rendered


# -

# # Test blankline removal

# +
with_blankline = """**<span style="color:purple">example&#95;func4</span>_()_**


Function to test if we can successfully remove doctest blanklines.
See https://docs.python.org/3.8/library/doctest.html#how-are-docstring-examples-recognized


#### Examples
```python
example_func4()
```
```
<BLANKLINE>
foo
```"""

without_blankline = '\n'.join('' if l == '<BLANKLINE>' else l for l in with_blankline.split('\n'))


def test_doctest_blankline_present():
    md = render_md_from_obj_docstring(example_func4, 'example_func4', remove_doctest_blanklines=False, examples_md_flavor='raw')
    assert md == with_blankline

def test_doctest_blankline_absent():
    md = render_md_from_obj_docstring(example_func4, 'example_func4', remove_doctest_blanklines=True, examples_md_flavor='raw')
    assert md == without_blankline
