npdoc_to_md converts the docstrings of Python objects into pretty markdown with the following functions available in **Command Line Interface** and **Python**:

* [render_obj_docstring](https://github.com/ThibTrip/npdoc_to_md/wiki/Render-object-docstring): extracts and formats **docstrings from importable paths** (e.g. "datetime.datetime")
  to Python objects directly
* [render_string](https://github.com/ThibTrip/npdoc_to_md/wiki/Render-string): extracts and formats docstrings via a **string/text with placeholders**
  (see documentation on placeholders below)
* [render_file](https://github.com/ThibTrip/npdoc_to_md/wiki/Render-file): extracts and formats docstrings via a **Markdown/template file with placeholders** (see documentation on placeholders below). Optionally saves converted text to a file
* [render_folder](https://github.com/ThibTrip/npdoc_to_md/wiki/Render-folder): same as `render_file` for a whole folder. Optionally saves to a destination folder, reproducing the structure of the source folder.
  File names are matched by a pattern (by default files with extensions ".md" or ".npmd" case insenstive)
* [logging](https://github.com/ThibTrip/npdoc_to_md/wiki/Logging): for configuring logging

In any case, the docstrings must follow the numpydoc style! See [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html) or [pandas docstring guide](https://pandas.pydata.org/docs/development/contributing_docstring.html)

# 1. Placeholders in markdown strings/files

Placeholders use JSON syntax with doubled curly brackets (`{{}}` instead of `{}`) and must be written in one line.

Here is an example of a placeholder (see the description of the parameters for these placeholders below):

`{{"obj":"pandas.DataFrame", "alias":"pd.DataFrame", "examples_md_lang":"raw", "remove_doctest_skip":"true", "remove_doctest_blanklines":true, "md_section_level":3}}`


# 1.1. Parameters for placeholders

* obj : **_str_**

  String of an importable Python object: function, method, ... or any object that has a docstring e.g. `"datetime.datetime"`,
  `"pandas"`, `"pandas.Timestamp"`

* alias : **_str, optional_**

  Custom namespace for the representation of the signature of the object
  e.g. `"pd.DataFrame"` instead of `"pandas.DataFrame"`

* examples_md_lang : **_str, default "raw"_**

  In which language to highlight code example outputs.

  **IMPORTANT**: [placeholders written directly in examples](#2-Placeholders-in-examples-for-output-languages) override this parameter!

  You can use any lang supported by markdown (python, markdown, html, ...) or one of the following
  special flags:
  * `raw`: a raw code block (no code highlighting)
  * **`markdown_rendered`**: does not make a code block, renders output (e.g. a table) in markdown


* remove_doctest_skip : **_bool, default False_**

  If True removes `# doctest: +SKIP` from examples (this is a marker for
  indicating doctest which tests to skip)

* remove_doctest_blanklines : **_bool, default False_**

  If True removes `<BLANKLINE>` from examples (this is a marker in doctest
  to indicate an empty line in a test)

* md_section_level : **_int, default 3_**

  Markdown title level for sections of the docstring (by default 3 which renders to `### {section}`).

  Please note that the level for the signature will be `md_section_level` - 1 (so by default 2).

* ignore_custom_section_warning : **_bool, default False_**

  When there is a custom section in the docstring, numpydoc raises a warning.
  You can set `ignore_custom_section_warning` to True to suppress it

* members: **_list[str] or None, default None__**

  When a list of members are given, in addition to rendering the docstring of a given object (`obj`)
  we will also render the docstrings of given members.

  We use a **special syntax** for indicating which members to document:
  * private$: flag that indicates private members (start with a single "_")
  * dunder$: flag that indicates "dunder" members, usually system method such as `__setattr__` (start with two or more "_")
  * public$: any member that does not fit under `private$` and `dunder$`
  * `+member` or `member`: member to include
  * `-member`: member to exlude

  Examples:

  `npdoc-to-md render-obj-docstring -obj some_library.TestClass ["public$", "-foo"]` -> all public members of class TestClass except `foo`

  `npdoc-to-md render-obj-docstring -obj some_library.TestClass ["private$", "foo", "+bar"]` -> all private members of class TestClass plus `foo` and `bar`

  Note: the order of flags/members is preserved

# 2. Placeholders in examples for output languages

Instead of or in addition to the parameter `examples_md_lang` you can use placeholders directly before examples to change the language
for highlighting example outputs.

The syntax is `{{language}}` e.g. `{{python}}`. The flags `{{raw}}` and `{{markdown_rendered}}` can also be used here (see parameter
`examples_md_lang` described above).

**IMPORTANT**: These placeholders overwrite the parameter `examples_md_lang`!

Here is how it looks like in the "Examples" sections of a docstring:

```
{{python}}
>>> print(1 + 1)
2

{{raw}}
>>> print('Hello')
Hello

{{html}}
>>> print('<b>Test</b>')
<b>Test</b>

>>> # no placeholder provided -> uses the language from parameter `examples_md_lang`
>>> print('Foo')
Foo
```

# 3. Notes

1. Custom sections are supported but they are interpreted as Markdown (like "Summary" and "Extended Summary").
2. GitHub does not support colors for markdown 😿. Object names (parameter `obj` of placeholders) should otherwise appear purple.
