## <span style="color:purple">npdoc\_to\_md.render\_obj\_docstring</span>_(obj: str, alias: Optional[str] = None, examples\_md\_lang: str = 'python', remove\_doctest\_blanklines: bool = False, remove\_doctest\_skip: bool = False, md\_section\_level: int = 3, ignore\_custom\_section\_warning: bool = False, members: Optional[List[str]] = None) -> str_

Converts the docstring of an object (e.g. function, class, method, module, ...)
to a pretty markdown string.

It uses the same parameters as the ones for placeholders described
in the wiki of the library.
See wiki folder at the root of the repo or https://github.com/ThibTrip/npdoc_to_md/wiki

### Examples

```python
from npdoc_to_md import render_obj_docstring

md = render_obj_docstring(obj="npdoc_to_md.testing.now_utc",
                          alias="now_utc",
                          examples_md_lang='raw',
                          remove_doctest_skip=True,
                          remove_doctest_blanklines=True,
                          md_section_level=3)
```