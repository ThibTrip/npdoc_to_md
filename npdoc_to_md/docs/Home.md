Welcome to npdoc_to_md's wiki!

# Getting started

## Docstring validity

All docstrings that you want converted to markdown must be valid according to pandas/numpy style docstring! See the following resources:
* https://pandas.pydata.org/pandas-docs/stable/development/contributing_docstring.html#docstring
* https://numpydoc.readthedocs.io/en/latest/format.html

## Placeholders to pull functions, classes or methods docstrings

Use placeholders in the markdown files you want to render to indicate for which functions, classes or methods you want to pull docstrings and convert them to markdown.

### Syntax

JSON dictionnary decorated by {} with the following keys (see examples below):
* "obj": name of an importable Python class, function or method
* <i>(optional)</i> "alias": namespace to use for the markdown render
    (e.g. pd.DataFrame instead of pandas.DataFrame). If this is not provided then the namespace is taken from the key "obj".
* <i>(optional)</i> "ex_md_flavor": In which language/flavor to render example outputs.
    See https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet#code-and-syntax-highlighting
    If not provided outputs are encapsulated by ````python```` to create a markdown Python code block. You can use any flavor
    you please or the special flag "raw" which will be a code block without flavor. If you choose "markdown" there is no encapsulation.
* <i>(optional)</i> "remove_doctest_blanklines": If True (default), replaces "<BLANKLINE>" used for doctest with an empty string.
    See https://docs.python.org/3.8/library/doctest.html#how-are-docstring-examples-recognized
    

A placeholder must be at the beginning of a line and this line cannot contain anything else!
    
* Bad example: <code>* {{"obj":"somefunc"}}</code>
* Good example: <code>{{"obj":"somefunc"}}</code>


### Examples

* <code>{{"obj":"pandas.DataFrame", "alias":"pd.DataFrame", "ex_md_flavor":"raw"}}</code>
* <code>{{"obj":"pandas.to_datetime"}}</code>

## Placeholders for example outputs

### Syntax
Before any example in a docstring you can define the markdown flavor/language for its output like this: {{LANGUAGE}} e.g. {{markdown}}, {{python}} or {{raw}} for no language which create a raw markdown code block.

When you do this for an example, this overrides the key "ex_md_flavor" in placeholders.

### Examples

```
{{markdown}}
>>> import pandas as pd
>>> df = pd.DataFrame({'A':[0,1]})
>>> print(df.to_markdown())
```
|    |   A |
|---:|----:|
|  0 |   0 |
|  1 |   1 |

```
{{python}}
>>> 2+2
```
```python
4
```

```
{{raw}}
>>> print('Hello')
```
```
'Hello'
```

# Usage

<b><i>Don't hesitate to post a GitHub issue if something is not clear!</i></b>

[Render the docstring of a function, class or method as a markdown string](https://github.com/ThibTrip/npdoc_to_md/wiki/Render-from-object)

[Render a markdown file with placeholders (e.g. <code>{{"obj":"pandas.DataFrame", "alias":"pd.DataFrame", "ex_md_flavor":"raw"}}</code>) as a string or a markdown file](https://github.com/ThibTrip/npdoc_to_md/wiki/Render-file)

[Previewing markdown strings with IPython!](https://github.com/ThibTrip/npdoc_to_md/wiki/Preview)

[Getting markdown files in a directory](https://github.com/ThibTrip/npdoc_to_md/wiki/List-markdown-files-in-dir)

[Example script I used to generate the documentation for npdoc_to_md](https://github.com/ThibTrip/npdoc_to_md/wiki/Example-script)