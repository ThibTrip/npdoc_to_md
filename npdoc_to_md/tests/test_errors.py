import pytest
import tempfile
from npdoc_to_md import render_md_file


# # Tests

def test_error_bad_placeholder(caplog):
    with tempfile.NamedTemporaryFile(suffix='.md', mode='w+') as tmp:
        tmp.write('{{"obj":"not_a_package.monkey"}}')
        tmp.seek(0)
        render_md_file(tmp.name, destination='test')
        assert 'Could not render line' in caplog.text
