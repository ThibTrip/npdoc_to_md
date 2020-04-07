# +
import doctest
from npdoc_to_md import helpers, core, utils

def test_helpers():
    doctest.testmod(helpers, verbose=True, raise_on_error=True)

def test_core():
    doctest.testmod(core, verbose=True, raise_on_error=True)

def test_utils():
    doctest.testmod(utils, verbose=True, raise_on_error=True)
