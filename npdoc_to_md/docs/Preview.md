You can preview markdown by using IPython! <code>pip install IPython</code>

# Simple example

```python
from IPython.display import display, Markdown

md = """
* yep
* this
* is
* **markdown**
"""

display(Markdown(md))
```
* yep
* this
* is
* **markdown**

## Note

If you are using a Jupyter notebook and if this is the last element of a cell then <code>Markdown(md)</code> is sufficient (no need for display).

# Examples with npdoc_to_md

```python
from pandas import Series # pip install pandas
from IPython.display import display, Markdown
from npdoc_to_md import render_md_from_obj_docstring

md = render_md_from_obj_docstring(Series, obj_namespace="pd.Series")
display(Markdown(md))
```
**<span style="color:purple">pd.Series</span>_(data=None, index=None, dtype=None, name=None, copy=False, fastpath=False)_**


#### Parameters
* data : <b><i>array-like, Iterable, dict, or scalar value</i></b>  Contains data stored in Series.
    
    .. versionchanged:: 0.23.0
       If data is a dict, argument order is maintained for Python 3.6
       and later.
* index : <b><i>array-like or Index (1d)</i></b>  Values must be hashable and have the same length as `data`.
    Non-unique index values are allowed. Will default to
    RangeIndex (0, 1, 2, ..., n) if not provided. If both a dict and index
    sequence are used, the index will override the keys found in the
    dict.
* dtype : <b><i>str, numpy.dtype, or ExtensionDtype, optional</i></b>  Data type for the output Series. If not specified, this will be
    inferred from `data`.
    See the :ref:`user guide <basics.dtypes>` for more usages.
* name : <b><i>str, optional</i></b>  The name to give to the Series.
* copy : <b><i>bool, default False</i></b>  Copy input data.



