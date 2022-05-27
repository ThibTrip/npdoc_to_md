"""
Expectations of how the docstrings of test objects in this library
should be rendered.

I put this in a separate file so that our tests aren't cluttered.

IMPORTANT: all the rendered docstrings must be Python raw strings!

See module `test_core.py`
"""

# # Common rendering options that were used to obtain the results below
#
# The example with public methods of a class will additionally use `members=['$public']` (see `test_core` module)

RENDERING_OPTIONS = dict(remove_doctest_blanklines=True,
                         remove_doctest_skip=True,
                         examples_md_lang='raw')

# # Rendered result of `documented_func_example`

documented_func_example_md = r"""
## <span style="color:purple">npdoc\_to\_md.testing.documented\_func\_example</span>_(a: int, b: int, \*, useless\_param=None, \_bad\_name\_param1=None, \_\_bad\_name\_param2=None, crazy\_typing\_param: Union[Dict[str, int], List[str]] = None, \*\*kwargs) -> int_

Example function that sums to integers. This function is used for pytest.
It does not really make sense, this is just for testing docstring rendering.

Some extended summary.

Multiline test.

### Parameters

* **a** : **_int_**

  First number.

  Multiline test.

* **b** : **_int_**

### Returns

* **c** : **_int_**

  Result of a + b.

  Multiline test.

### Raises

* **_TypeError_**

  If a or b is not a number.

  Multiline test.

### Warns

* **_UserWarning_**

  Never occurs (this is just an example)

  Multiline test.

### Other Parameters

* **useless\_param**

  Some useless parameter.

  Multiline test.

* **\_bad\_name\_param1**

* **\_\_bad\_name\_param2**

* **crazy\_typing\_param**

  Parameter with complex typing

* **optional\_type\_param**

  Parameter with optional typing

### See Also

* **empty\_function, EmptyClass, empty\_doc\_sections\_function, EmptyDocSectionsClass**

  Other useless functions.
  Numpydoc deletes line breaks for section "See Also" so no multiline test here...
  The next function I put in this section will have no description.

* **now\_utc**

### Notes

Some notes.

Multiline test.

### Warnings

Cautionnary notes for the user.
More warning notes.

Multiline test.

### References

[0] Me

Multiline test.

### Examples

We are going to try to break our library by:
1. Putting text before examples or not
2. Separating examples by line breaks (also with irrelevant leading spaces) or not

We'll then check if the library still manages to separate examples properly

* example 1
```python
documented_func_example(1, 1)
```
```python
2
```

* example 2
```python
documented_func_example(2, 2)
```
```python
4
```

---

#### Examples unrelated to the function

* test rendered markdown
```python
import pandas as pd
df = pd.DataFrame({'A':[1, 2]})
print(df.to_markdown())
```
|    |   A |
|---:|----:|
|  0 |   1 |
|  1 |   2 |

* test raw code block
```python
print('Hello world!')
```
```
Hello world!
```

* test non rendered markdown
```python
print('# some markdown string\n* test')
```
```markdown
# some markdown string
* test
```

```python
print('test')
```
```
test
```
```python
print('foo\n')
```
```
foo

```
""".strip()

# # Rendered result of `documented_generator_func_example`

documented_generator_func_example_md = r"""
## <span style="color:purple">npdoc\_to\_md.testing.documented\_generator\_func\_example</span>_(nb\_vals=10)_

Generator example (for testing the parsing of Yields and Receives sections).
Simply yields a range from 0 to `nb_vals`.

### Yields

* **i** : **_int_**

  Incrementing integers.

  Multiline test.

### Receives

* **nb\_vals** : **_int, default 10_**

  Number of values to yield.

  Multiline test.

### Examples

```python
for i in documented_generator_func_example(2):
   print(i)
```
```
0
1
```""".strip()

# # Rendered result of `DocumentedClassExample` with public methods

DocumentedClassExampleMd = r"""
## <span style="color:purple">npdoc\_to\_md.testing.DocumentedClassExample</span>_(first\_name: str, last\_name: str) -> None_

Example dataclass representing a person. This class is used for pytest.
It does not really make sense, this is just for testing docstring rendering.

### Attributes

* **full\_name** : **_str_**

  first name + last name (both names in title case and separated by a space).

  Multiline test.

### Examples

```python
ex = DocumentedClassExample(first_name='John', last_name='Doe')
ex.full_name
```
```
'John Doe'
```

## <span style="color:purple">npdoc\_to\_md.testing.DocumentedClassExample.example\_method</span>_() -> None_

Prints the first name defined in the instance.
This is a test for rendering docstrings of methods.

### Examples

```python
d = DocumentedClassExample('John', 'Doe')
d.example_method()
```
```
John
```

## <span style="color:purple">npdoc\_to\_md.testing.DocumentedClassExample.example\_static\_method</span>_() -> List[str]_

Prints the names of the dataclass fields.
This is a test for rendering docstrings of staticmethods.

### Examples

```python
DocumentedClassExample.example_static_method()
```
```
['first_name', 'last_name']
```

```python
d = DocumentedClassExample('John', 'Doe')
d.example_static_method()
```
```
['first_name', 'last_name']
```

## <span style="color:purple">npdoc\_to\_md.testing.DocumentedClassExample.full\_name</span>

Returns the full name using the names part defined in the instance.
This is a test for rendering docstrings of properties.

### Returns

* **_str_**

  Full name

### Examples

```python
ex = DocumentedClassExample(first_name='john', last_name='doe')
ex.full_name
```
```
'John Doe'
```

## <span style="color:purple">npdoc\_to\_md.testing.DocumentedClassExample.test\_class\_method</span>_() -> 'DocumentedClassExample'_

Returns a "John Doe" instance of the class.
This is a test for rendering docstrings of class methods.

### Examples

```python
DocumentedClassExample.test_class_method()
```
```
DocumentedClassExample(first_name='John', last_name='Doe')
```
""".strip()

# # Rendered result of `npdoc_to_md.testing` module

testing_module_md = r"""
## <span style="color:purple">npdoc\_to\_md.testing</span>

Dummy objects (classes, functions, ...) for demos of the library and tests

### Notes

The docstring of this module will be used for docstring rendering tests in pytest.
Which is why I am also going to include some examples here and a custom section
"Functions".

### Functions

* create_random_table
  Returns a random table (pandas DataFrame)
* now_utc
  Returns the current date and time in UTC
* ...

### Examples

```python
from npdoc_to_md.testing import DocumentedClassExample

ex = DocumentedClassExample(first_name='John', last_name='Doe')
ex.full_name
```
```
'John Doe'
```""".strip()

# # Rendered results of objects with empty docstrings or empty sections

# +
empty_function_md = r'## <span style="color:purple">npdoc\_to\_md.testing.empty\_function</span>_()_'
EmptyClassMd = r'## <span style="color:purple">npdoc\_to\_md.testing.EmptyClass</span>_()_'
EmptyClassDictMd = r'## <span style="color:purple">npdoc\_to\_md.testing.EmptyClass.\_\_dict\_\_</span>'  # render of __dict__ method's docstring
empty_doc_sections_function_md = r"""
## <span style="color:purple">npdoc\_to\_md.testing.empty\_doc\_sections\_function</span>_()_



### Parameters



### Yields



### Receives



### Raises



### Warns



### Other Parameters



### Attributes



### Methods
""".strip()

EmptyDocSectionsClass_md = r"""
## <span style="color:purple">npdoc\_to\_md.testing.EmptyDocSectionsClass</span>_()_



### Parameters



### Yields



### Receives



### Raises



### Warns



### Other Parameters



### Attributes



### Methods
""".strip()

none_md = r'## <span style="color:purple">None</span>'  # rendered version of None object
builtins_none_md = r'## <span style="color:purple">builtins.None</span>'  # rendered version of None object imported from builtins
