[![CircleCI](https://circleci.com/gh/ThibTrip/npdoc_to_md/tree/master.svg?style=svg&circle-token=e33f9d9e628fde342e9acd4c43c2c939780bf1f0)](https://circleci.com/gh/ThibTrip/npdoc_to_md/tree/master) [![codecov](https://codecov.io/gh/ThibTrip/npdoc_to_md/branch/master/graph/badge.svg)](https://codecov.io/gh/ThibTrip/npdoc_to_md) [![PyPI version](https://img.shields.io/pypi/v/npdoc_to_md)](https://img.shields.io/pypi/v/npdoc_to_md)

# npdoc_to_md

Turns numpy docstrings to pretty markdown.

# Table of contents

[Features](#Features)

[Caveats](#Caveats)

[Installation](#Installation)

[Demos](#Demos)

[Usage](#Usage)

[Contributing](#Contributing)

[Generating the documentation](#Generating-the-documentation)

[Testing](#Testing)

# Features

* Very easy to use
* Flexible rendering for example outputs (render a markdown table, python code, raw code etc.) on a per-example basis or a per-docstring basis
* Provides file rendering with very simple placeholders

# Caveats

* GitHub does not support colors for markdown 😿

# Installation

<code>pip install npdoc_to_md</code>

# Demos

## First demo: Demonstration with the docstring of pandas.Series.

### Before

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

### After

{{"obj":"pandas.DataFrame", "alias":"pd.DataFrame", "ex_md_flavor":"raw"}}

## Second demo: the library pangres (also from me) which uses markdown tables in examples!

See https://github.com/ThibTrip/pangres/wiki/Upsert#examples

# Usage

Head over to npdoc_to_md's [wiki](https://github.com/ThibTrip/npdoc_to_md/wiki)!

# Contributing

Pull requests/issues are welcome.

# Generating the documentation

All the documentation (this README and the wiki) needs to be **generated** from files contained in <b><code>./npdoc_to_md/docs</code></b>.

This is easy to do with the included script <code>./npdoc_to_md/docs/generate_documentation.py</code>:

1. Clone the repo if you have not already (<code>https://github.com/ThibTrip/npdoc_to_md.git</code>)
2. Clone the wiki (<code>git clone https://github.com/ThibTrip/npdoc_to_md.wiki.git</code>)
3. Execute the commands below in your terminal (while located in the root folder of npdoc_to_md that you have cloned on your computer). Replace <b><code>NPDOC_TO_MD_PATH</code></b> with the path where you cloned npdoc_to_md's repo and replace <b><code>WIKI_FOLDER_PATH</code></b> with the path to where you cloned the wiki. Note: don't mind the errors with the line "{{raw}}" and "{{python}}" for the file "Home.md" (since npdoc_to_md is rendering its own documentation things get a little weird).

```
cd ./npdoc_to_md/docs
python generate_documentation.py NPDOC_TO_MD_PATH WIKI_FOLDER_PATH
```

4. Commit the changes in the wiki


**IMPORTANT:** Do not modify the wiki or the README directly! Modify the files in <b><code>./npdoc_to_md/docs</code></b> instead.

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
pytest -s -vv npdoc_to_md --cov=./npdoc_to_md --doctest-modules
```