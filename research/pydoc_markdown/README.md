Here I am trying out the library [pydoc-markdown](https://github.com/NiklasRosenstein/pydoc-markdown). Follow the instructions below to test the results.


# Installation

First, install the library, preferably in the conda environment at the root of the repo, and then:

```
pip install novella pydoc-markdown[novella]
```

# Usage

```
novella --serve
```

Sadly this does not work... I tried putting all the files here (`build.novella` and `content/*`) in the root of the repo and when I tried again I got this error:

```
ValueError: no next element for the walker to move to
```

Using the API with the code below I got the same error as above:

```python
from pydoc_markdown.interfaces import Context
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer

context = Context(directory='.')
loader = PythonLoader(search_path=['../../'])
renderer = MarkdownRenderer(render_module_header=False)

loader.init(context)
renderer.init(context)

modules = loader.load()
print(renderer.render_to_string(modules))
```

Also no luck with this command executed at the root of the repo:

```
pydoc-markdown -I src -m npdoc_to_md.core --render-toc > test.md
```
