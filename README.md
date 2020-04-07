# npdoc_to_md

Turns numpy docstrings to pretty markdown.

# Table of contents

[Features](#Features)

[Caveats](#Caveats)

[Installation](#Installation)

[Demo](#Demo)

&nbsp;&nbsp;&nbsp;&nbsp;[Before](#Before)

&nbsp;&nbsp;&nbsp;&nbsp;[After](#After)

[Usage](#Usage)

[Contributing](#Contributing)

[Testing](#Testing)

# Features

* Very easy to use
* Flexible rendering for example outputs (render a markdown table, python code, raw code etc.) on a per-example basis or a per-docstring basis
* Provides file rendering with very simple placeholders

# Caveats

* GitHub does not support colors for markdown 😿

# Installation

Clone the repository with <code>git clone https://github.com/ThibTrip/npdoc_to_md.git</code>. Then while still in the same folder install with pip <code>pip install ./npdoc_to_md</code>.

The repository shall be added to PyPI soon 🐍.

# Demo

Demonstration with the docstring of pandas.Series.

## Before

```
Two-dimensional, size-mutable, potentially heterogeneous tabular data.

Data structure also contains labeled axes (rows and columns).
Arithmetic operations align on both row and column labels. Can be
thought of as a dict-like container for Series objects. The primary
pandas data structure.

Parameters
----------
data : ndarray (structured or homogeneous), Iterable, dict, or DataFrame
    Dict can contain Series, arrays, constants, or list-like objects.

    .. versionchanged:: 0.23.0
       If data is a dict, column order follows insertion-order for
       Python 3.6 and later.

    .. versionchanged:: 0.25.0
       If data is a list of dicts, column order follows insertion-order
       for Python 3.6 and later.

index : Index or array-like
    Index to use for resulting frame. Will default to RangeIndex if
    no indexing information part of input data and no index provided.
columns : Index or array-like
    Column labels to use for resulting frame. Will default to
    RangeIndex (0, 1, 2, ..., n) if no column labels are provided.
dtype : dtype, default None
    Data type to force. Only a single dtype is allowed. If None, infer.
copy : bool, default False
    Copy data from inputs. Only affects DataFrame / 2d ndarray input.

See Also
--------
DataFrame.from_records : Constructor from tuples, also record arrays.
DataFrame.from_dict : From dicts of Series, arrays, or dicts.
read_csv
read_table
read_clipboard

Examples
--------
Constructing DataFrame from a dictionary.

>>> d = {'col1': [1, 2], 'col2': [3, 4]}
>>> df = pd.DataFrame(data=d)
>>> df
   col1  col2
0     1     3
1     2     4

Notice that the inferred dtype is int64.

>>> df.dtypes
col1    int64
col2    int64
dtype: object

To enforce a single dtype:

>>> df = pd.DataFrame(data=d, dtype=np.int8)
>>> df.dtypes
col1    int8
col2    int8
dtype: object

Constructing DataFrame from numpy ndarray:

>>> df2 = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
...                    columns=['a', 'b', 'c'])
>>> df2
   a  b  c
0  1  2  3
1  4  5  6
2  7  8  9
```

## After

**<span style="color:purple">pd.DataFrame</span>_(data=None, index: Union[Collection, NoneType] = None, columns: Union[Collection, NoneType] = None, dtype: Union[str, numpy.dtype, ForwardRef('ExtensionDtype'), NoneType] = None, copy: bool = False)_**


#### Parameters
* data : <b><i>ndarray (structured or homogeneous), Iterable, dict, or DataFrame</i></b>  Dict can contain Series, arrays, constants, or list-like objects.
	
	.. versionchanged:: 0.23.0
	   If data is a dict, column order follows insertion-order for
	   Python 3.6 and later.
	
	.. versionchanged:: 0.25.0
	   If data is a list of dicts, column order follows insertion-order
	   for Python 3.6 and later.
* index : <b><i>Index or array-like</i></b>  Index to use for resulting frame. Will default to RangeIndex if
	no indexing information part of input data and no index provided.
* columns : <b><i>Index or array-like</i></b>  Column labels to use for resulting frame. Will default to
	RangeIndex (0, 1, 2, ..., n) if no column labels are provided.
* dtype : <b><i>dtype, default None</i></b>  Data type to force. Only a single dtype is allowed. If None, infer.
* copy : <b><i>bool, default False</i></b>  Copy data from inputs. Only affects DataFrame / 2d ndarray input.

#### See Also
* DataFrame.from_records : Constructor from tuples, also record arrays.
* DataFrame.from_dict : From dicts of Series, arrays, or dicts.
* read_csv
* read_table
* read_clipboard

#### Examples
Constructing DataFrame from a dictionary.

```python
d = {'col1': [1, 2], 'col2': [3, 4]}
df = pd.DataFrame(data=d)
df
```
```
col1  col2
0     1     3
1     2     4
```

Notice that the inferred dtype is int64.

```python
df.dtypes
```
```
col1    int64
col2    int64
dtype: object
```

To enforce a single dtype:

```python
df = pd.DataFrame(data=d, dtype=np.int8)
df.dtypes
```
```
col1    int8
col2    int8
dtype: object
```

Constructing DataFrame from numpy ndarray:

```python
df2 = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                   columns=['a', 'b', 'c'])
df2
```
```
a  b  c
0  1  2  3
1  4  5  6
2  7  8  9
```

# Usage

Head over to npdoc_to_md's [wiki](https://github.com/ThibTrip/npdoc_to_md/wiki)!

# Testing

Clone npdoc_to_md then set your curent working directory to the root of the cloned repository folder. Then use the commands below:

```
# 1. Create and activate the build environment
conda env create -f environment.yml
conda activate npdoc_to_md-dev
# 2. Install npdoc_to_md in editable mode (changes are reflected upon reimporting)
pip install -e .
# 3. Run pytest
# -s prints stdout
# -v prints test parameters
# --cov=./npdoc_to_md shows coverage only for npdoc_to_md
pytest -s -v npdoc_to_md --cov=./npdoc_to_md
```