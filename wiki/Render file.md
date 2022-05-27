## <span style="color:purple">npdoc\_to\_md.render\_file</span>_(source: str, destination: Optional[str] = None, ignore\_errors: bool = False) -> Union[npdoc\_to\_md.core.RenderedFile, npdoc\_to\_md.core.RenderedFileCLI]_

Reads markdown file at path `source` and replaces placeholders defined in this library
with the corresponding docstrings. It then returns the "converted" text.

If a `destination` is given we save the converted text at this path.

See wiki folder at the root of the repo or https://github.com/ThibTrip/npdoc_to_md/wiki
for the placeholders syntax.

### Parameters

* **source**

  Path to the markdown file

* **destination**

  If None only returns a converted markdown string.
  Otherwise it also creates or overwrites the file
  at this path with the converted markdown string.

* **ignore\_errors**

  Same logic as in function `render_string` (see its docstring)

### CLI Examples

Note that "-" and "_" are interchangeable

```
$ npdoc-to-md render-file -source "./docs/Render file.npmd" --destination "./docs/Render file.md"
```

Since we are using python-fire for the CLI it is possible to access attributes
of the class (RenderedFile) instance that is returned. In the example below
we are acccessing the attribute `rendered_text`:

```
$ npdoc-to-md render-file -source "./docs/Render file.npmd" --destination "./docs/Render file.md" - rendered-text
```

See also the python-fire guide: https://github.com/google/python-fire/blob/master/docs/guide.md


### Returns

* **_npdoc_to_md.RenderedFile | npdoc_to_md.RenderedFileCLI_**

  Returns RenderedFile object if using this function in Python.
  Returns RenderedFileCLI if using this function in CLI.
  See docstring of these objects.

### Examples

```python
from npdoc_to_md import render_file

source = "./README.md"
destination = "./README_converted.md"
rendered_file = render_file(source=source, destination=destination) # doctest: +SKIP
```