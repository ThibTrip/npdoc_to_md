## <span style="color:purple">npdoc\_to\_md.render\_folder</span>_(source: str, destination: Optional[str] = None, recursive: bool = False, ignore\_errors: bool = False, pattern: Optional[str] = None, case\_sensitive: bool = False) -> Union[List[npdoc\_to\_md.core.RenderedFile], npdoc\_to\_md.core.RenderedFilesCLI]_

Reads all markdown files in the folder at path `source`
and for each markdown file, replaces placeholders defined in this library
with the corresponding docstrings.

If a `destination` folder is given we also save converted files there using
the same folder structure (case of `recursive=True`) and also the same
file names, except the extensions that always get converted to ".md"
(unless they already matched ".md" case insensitive) e.g.:
* `some_lib/docs_templates/Home.npmd` -> `some_lib/docs/Home.md`
* `some_lib/docs_templates/Logging.MD` -> `some_lib/docs/Logging.MD`
* `some_lib/docs_templates/cool_subpackage/Home.npmd` -> `some_lib/docs/cool_subpackage/Home.md`

See wiki folder at the root of the repo or https://github.com/ThibTrip/npdoc_to_md/wiki
for the placeholders syntax.

### Parameters

* **source**

  Path to the folder containing markdown files

* **destination**

  If None no file operations is done but you still get the result
  of the rendering (see sections Examples | CLI Examples and Returns)

* **recursive**

  If False only looks for markdown files directly in folder `source`
  otherwise also looks inside subfolders

* **ignore\_errors**

  Same logic as in function `render_string` (see its docstring)

* **pattern**

  Regex pattern for matching file names in folder `source`
  e.g. "(\.md|\.txt)$" (file names with the extension ".md"
  or ".txt")

  By default we use a regex pattern matching "md" and "npmd"
  extensions. See attributes `template_files` and `template_files_insensitive`
  of class `npdoc_to_md.helpers.Patterns`

* **case\_sensitive**

  Whether the `pattern` is case sensitive. By default this is False (`pattern` is
  case insensitive)

### CLI Examples

Note that "-" and "_" are interchangeable

```
$ npdoc-to-md render-folder -source "./docs" --destination "./docs" --ignore-errors --recursive
```

Since we are using python-fire for the CLI it is possible to work with the returned object (a list
of RenderedFileCLI instances). In the example below we are acccessing the attribute `rendered_text`
of the first item:

```
$ npdoc-to-md render-folder -source "./docs" --destination "./docs" --ignore-errors --recursive - 0 - rendered_text
```

See also the python-fire guide: https://github.com/google/python-fire/blob/master/docs/guide.md


### Returns

* **_list[npdoc_to_md.RenderedFile] | RenderedFilesCLI_**

  Returns list[RenderedFile] if using this function in Python.
  Returns RenderedFilesCLI if using this function in the CLI.

  See docstring of these objects.

### Examples

```python
from npdoc_to_md import render_folder

source = "./docs_templates"
destination = "./docs"
rendered_files = render_folder(source=source, destination=destination) # doctest: +SKIP
```