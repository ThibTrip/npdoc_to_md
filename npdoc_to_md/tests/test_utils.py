import os
from npdoc_to_md import get_markdown_files_in_dir


# # Test get_markdown_files_in_dir

def test_get_markdown_files_in_dir():
    with open('test.md', mode='w', encoding='utf-8') as fh:
        fh.write('foo')
    assert os.path.isfile('test.md')
    files_and_names = get_markdown_files_in_dir('.')
    assert 'test.md' in files_and_names.values()
    os.remove('test.md')
