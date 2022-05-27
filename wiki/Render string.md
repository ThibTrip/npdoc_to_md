## <span style="color:purple">npdoc\_to\_md.render\_string</span>_(string: str, ignore\_errors: bool = False) -> str_

Returns a markdown string where placeholders defined in this library have
been replaced with the corresponding docstrings rendered in Markdown.

See wiki folder at the root of the repo or https://github.com/ThibTrip/npdoc_to_md/wiki
and the examples for the placeholders syntax.

### Parameters

* **string**

  String with markdown syntax (we will split it in lines)
  containing (or not) placeholders defined in this library

* **ignore\_errors**

  If True only logs errors relative to converting placeholders
  in the string otherwise raises such errors.
  Also, placeholders that failed to convert will
  be unchanged in the resulting text

  Note that any string that begings with "{{" and ends with "}}" on the
  same line is interpreted as a placeholder by the library.

### CLI Examples

Note that "-" and "_" are interchangeable.

While I do make this method available for the CLI, if you are going to do similar
things as the examples below, I would suggest looking at the other functions of
the library for generating documentation. Indeed, unless you are in Bash and can use a multiline string,
the escaping is tricky as you can see below.

IMPORTANT: do not put spaces in the placeholders (e.g. between commas) otherwise the parsing would fail (because
space is a character used to separate arguments)

Bash example:

```
$ STRING='"{{\"obj\":\"npdoc_to_md.testing.DocumentedClassExample\",\"remove_doctest_blanklines\":true,\"remove_doctest_skip\":true,\"examples_md_lang\":\"raw\",\"members\":[\"public$\"]}}"'
$ npdoc-to-md render-string -string "$STRING"
```

Command Prompt example (Windows):

```
$ set STRING='"{{\"obj\":\"npdoc_to_md.testing.DocumentedClassExample\",\"remove_doctest_blanklines\":true,\"remove_doctest_skip\":true,\"examples_md_lang\":\"raw\",\"members\":[\"public$\"]}}"'
$ npdoc-to-md render-string -string %STRING%
```

Bash example (multiline):

```
$ STRING='Demo:
> {{"obj":"npdoc_to_md.testing.DocumentedClassExample", "remove_doctest_blanklines":true, "md_section_level":3, "members":["public$"]}}'
$ npdoc-to-md render-string -string "$STRING"
```


### Examples

```python
from npdoc_to_md import render_string

text = """
Here is a demo of npdoc_to_md.render_string. The placeholder
below will be converted to a docstring in markdown:

---

{{"obj":"npdoc_to_md.testing.now_utc", "alias":"now_utc"}}
"""
md = render_string(string=text)
```
```python

```
```python
# demonstrating "ignore_errors": this raises no error even though we are referring to a non existent object
md = render_string(string='{{"obj":"some_object_that_does_not_exist"}}', ignore_errors=True)
```