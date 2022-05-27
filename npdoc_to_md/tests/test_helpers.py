# +
"""
Tests the helpers module
"""
import pytest
import re
import os
import tempfile
from pathlib import Path

# local imports
from npdoc_to_md.helpers import FileOperations, Patterns


# -

# # Test patterns

@pytest.mark.parametrize('pattern_attr, string, expected', [('console_py', '>>> print("hello")', '>>> '),
                                                            ('console_py', '...     2 + 2', '... '),
                                                            ('doctest_skip', '>>> print("hello") #doctest: +SKIP', ' #doctest: +SKIP'),
                                                            ('blankline', ' <BLANKLINE> ', ' <BLANKLINE> '),
                                                            ('self_or_cls', 'Foo(self, a:int, b:int)', 'self, '),
                                                            ('template_files', 'README.md', '.md'),
                                                            ('template_files', 'README.MD', None),  # does not match
                                                            ('template_files_insensitive', 'README.md', '.md'),
                                                            ('template_files_insensitive', 'README.MD', '.MD')])
def test_patterns(pattern_attr, string, expected):
    """
    Tests regex patterns listed as attributes in class npdoc_to_md.helpers.Patterns
    """
    pat:re.Pattern = getattr(Patterns, pattern_attr)
    if expected is None:
        assert not pat.search(string)
    else:
        assert pat.search(string).group(0) == expected


# # Test file listing

# +
test_pattern_file_listing = re.compile(r'\.txt$')


@pytest.mark.parametrize('recursive', [True, False], ids=['recursive', 'non recursive'])
def test_file_listing(recursive):
    with tempfile.TemporaryDirectory() as tmpdirpath:

        # create test structure
        # we will have a file 1 under root and a file 2 under a subfolder called "subfolder"
        filename1, subfoldername, filename2 = 'foo.txt', 'subfolder', 'bar.txt'
        with open(os.path.join(tmpdirpath, filename1), mode='w', encoding='utf-8') as fh:
            fh.write('test')
        os.mkdir(os.path.join(tmpdirpath, subfoldername))
        with open(os.path.join(tmpdirpath, subfoldername, filename2), mode='w', encoding='utf-8') as fh:
            fh.write('test')

        # list paths
        filepaths = FileOperations.list_files(folder=tmpdirpath, recursive=recursive, pattern=test_pattern_file_listing)
        nb_items_expected = 2 if recursive else 1
        assert len(filepaths) == nb_items_expected

        # check paths integrity

        # check file 1 is present
        assert any(Path(f).name == filename1 for f in filepaths)

        # check file 2 is present (when recursive) and check its parents
        if not recursive:
            return
        candidates = list(filter(lambda f: Path(f).name == filename2, filepaths))
        if len(candidates) == 0:
            raise AssertionError(f'Filepath of second test file seems absent. All paths:\n{filepaths}')  # pragma: no cover
        assert len(candidates) == 1, 'Multiple paths for second test file ?!'
        path_obj = Path(candidates[0])
        assert path_obj.parent.name == subfoldername
        assert path_obj.parent.parent.name == Path(tmpdirpath).name


# -

# # Test switching folders

# +
params_switch_folders = [
    ('D:/', 'C:/Test', 'D:/foo.md', 'C:/Test/foo.md'),
    ('D:/', 'C:/Test', 'D:/Subfolder/foo.md', 'C:/Test/Subfolder/foo.md'),
    ('/home/my_lib/docs', '/home/test', '/home/my_lib/docs/foo.md', '/home/test/foo.md'),
    ('/home/my_lib/docs', '/home/test', '/home/my_lib/docs/subfolder/foo.md', '/home/test/subfolder/foo.md')
]


@pytest.mark.parametrize('source, destination, filepath, expected', params_switch_folders)
def test_switch_folder(source, destination, filepath, expected):
    new_filepath = FileOperations.switch_folder(source_folder=source, destination_folder=destination,
                                                filepath=filepath, create_missing_dirs=False)
    # Path allows us to make OS agnostic comparisons
    assert Path(new_filepath) == Path(expected)
