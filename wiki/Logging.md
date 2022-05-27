You can set the logging level of the library by setting the environment variable `NPDOC_TO_MD_LOG_LEVEL` before the first call to one of the functions (ideally do it even before importing the library).

```python
import logging
import os
os.environ['NPDOC_TO_MD_LOG_LEVEL'] = str(logging.WARNING)
from npdoc_to_md import render_obj_docstring

# now any logs under the WARNING level will be hidden for this library
# render_obj_docstring(...)
```