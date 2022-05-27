[![example workflow](https://github.com/ThibTrip/npdoc_to_md/actions/workflows/main_workflow.yml/badge.svg)](https://github.com/ThibTrip/npdoc_to_md/actions/workflows/main_workflow.yml)
[![codecov](https://codecov.io/gh/ThibTrip/npdoc_to_md/branch/master/graph/badge.svg)](https://codecov.io/gh/ThibTrip/npdoc_to_md)
[![PyPI version](https://img.shields.io/pypi/v/npdoc_to_md)](https://img.shields.io/pypi/v/npdoc_to_md)
[![Documentation](https://img.shields.io/badge/wiki-documentation-forestgreen)](https://github.com/ThibTrip/npdoc_to_md/wiki)
[![Made withJupyter](https://img.shields.io/badge/Made%20with-Jupyter-orange?logo=Jupyter)](https://jupyter.org/try)

# npdoc_to_md
![logo](logo.png)

_Thanks to [freesvg.org](https://freesvg.org/) for the logo assets_

Automatic documentation tool using Markdown and Python docstrings written with the [**numpydoc style**](https://numpydoc.readthedocs.io/en/latest/format.html).

This library **does not generate a website**! It converts **template** strings/files/folders written in **Markdown**. The result of that can be used for instance for **GitHub or Gitlab Wiki**.

The features (see below) are somewhat basic. If you need more advanced features you might want to look into my suggestions for [other documentation tools](#Other-documentation-tools).

# Features

* **Easy to use**: just place a few placeholders in template files and **convert a file or a folder of templates** with a **single command**
* Supports **all sections** of a docstring in numpydoc style + **custom sections** (they'll be read as Markdown)
* Flexible **language highlighting** for **example outputs** (render a markdown table, python code, raw code etc.) on a per-example basis or a per-docstring basis

# Requirements

* Python 3.7+ (besides dataclasses that can be backported with `pip install dataclasses` there would be too many changes for 3.6 compatibility which is obsolete anyways)
* dependencies of this library (see [requirements.txt](./requirements.txt) and [Installation section](#Installation))

# Installation

```
pip install npdoc_to_md
```

Install the [**fire library**](https://github.com/google/python-fire) from Google to **use the CLI** (recommended)

```
pip install fire
```

# Quickstart

For more features (e.g. rendering a whole folder in a single command) and explanations on the placeholders (lines
surrounded by `{{ }}`), head over to the [documentation](https://github.com/ThibTrip/npdoc_to_md/wiki).

## 1. Make a template in Markdown

**`.npmd`** is the recommended file extension for template files using this library but that's entirely up to you.

Content of our example template **`Home.npmd`**:

```markdown
# My super cool library

## Some dummy function

{{"obj":"npdoc_to_md.testing.create_random_table", "alias":"create_random_table", "examples_md_lang":"markdown_rendered", "remove_doctest_skip":true, "remove_doctest_blanklines":true, "md_section_level":3}}
```

## 2. Render the template

From a terminal:

`$ npdoc-to-md render-file -source "Home.npmd" --destination "Home.md"`

From Python:

```python
from npdoc_to_md import render_file

render_file(source='Home.npmd', destination='Home.md')
```

## 3. Enjoy the result 🐍

### Before

```
Creates a random table

Parameters
----------
nb_rows
    How many rows to generate

Examples
--------
>>> from npdoc_to_md.testing import TestFunctions
>>>
>>> df = TestFunctions.create_random_table()
>>> print(df.to_markdown(index=False))  # doctest: +SKIP
|   A |   B |   C |   D |
|----:|----:|----:|----:|
|  67 |  14 |  78 |  77 |
|  12 |  96 |  69 |  54 |
|  81 |  13 |  55 |  18 |
|  15 |  15 |  88 |  64 |
|  48 |  68 |  36 |  10 |
```

### After

___

**<span style="color:purple">create\_random\_table</span>_(nb\_rows: int = 5) -> 'pandas.DataFrame'_**

Creates a random table

### Parameters
* **nb\_rows**

  How many rows to generate


### Examples
```python
from npdoc_to_md.testing import TestFunctions

df = TestFunctions.create_random_table()
print(df.to_markdown(index=False))
```

|   A |   B |   C |   D |
|----:|----:|----:|----:|
|  67 |  14 |  78 |  77 |
|  12 |  96 |  69 |  54 |
|  81 |  13 |  55 |  18 |
|  15 |  15 |  88 |  64 |
|  48 |  68 |  36 |  10 |

___

# Testing

```
# 1. Create and activate the build environment
conda env create -f environment.yml
conda activate npdoc_to_md-dev
# 2. Install npdoc_to_md in editable mode (changes are reflected upon reimporting)
pip install -e .
# 3. Run pytest
pytest -sv npdoc_to_md --cov=npdoc_to_md --doctest-modules
```

# Development

I develop the library inside of **Jupyter Lab** using the [**jupytext**](https://github.com/mwouts/jupytext) extension.

I recommend using this extension for the best experience.
It will split code blocks within modules in notebook cells and will allow **interactive development**.

If you wish you can also use the provided **conda environment** (see `environment.yml` file) inside of Jupyter Lab/Notebook
thanks to [**nb_conda_kernels**](https://github.com/Anaconda-Platform/nb_conda_kernels).

# Other documentation tools

Note that all libraries below **produce a website and not markdown files** like `npdoc_to_md` does. I also wrote some feedback after trying them for `npdoc_to_md` (see the [research folder](./research)). Obviously this is not an exhaustive list of documentation tools.

* [mkdocstrings](https://github.com/mkdocstrings/mkdocstrings): this library seems to have a few problems with numpydoc style docstrings
* [pydoc-markdown](https://github.com/NiklasRosenstein/pydoc-markdown): does not seem to support numpydoc style docstrings (see this [issue](https://github.com/NiklasRosenstein/pydoc-markdown/issues/251)). I have not gotten it to work yet because I have an error with the most basic configuration (`no next element for the walker to move to`)
* [sphinx](https://www.sphinx-doc.org/en/master/): sphinx works quite well with the simple example I provided. I didn't manage to get markdown inside docstrings to work though.

# Motivation

**Sphinx** is what motivated me to make such a library several years ago (it was first private for a long time).

I was never 100% satisfied with the results (I had much more complex cases including the presence of subpackages) despite a lot of time spent tweaking sphinx.
I also did not like the idea of having to **host a website for private libraries** and then also having to protect it with a **login**.

There is probably a library I could use as backend instead of doing a big part of the parsing myself or maybe even a library that could replace this one.
Feel free to contact me if you come up with something interesting.
This was a great learning project though and I am very happy with the current results.