"""
Helpers for the various modules of the library
"""
import os
import re
from pathlib import Path
from typing import Iterable, List


# # Regex patterns

class Patterns:
    """
    All regex patterns used in the library

    Attributes
    ----------
    console_py
        Matches inputs in docstring examples
    doctest_skip
        Matches "# doctest: +SKIP" marker of doctest in docstring examples
    blankline
        Matches "<BLANKLINE>" marker of doctest in docstring examples
    self_or_cls
        Matches special arguments "self" or "cls" that we remove from signatures.
        Also matches any subsequent character we'll have to remove (following space(s)
        and comma(s))
    template_files
        Matches file extensions ".np" and ".md" case sensitive
    template_files_insensitive
        Same as attribute `template_files` but case insensitive
    """
    console_py = re.compile(r'^(\>\>\> ?|\.\.\. ?)')
    doctest_skip = re.compile(r' *\# *doctest: *\+SKIP *$')
    blankline = re.compile(r'^ *\<BLANKLINE\> *$')
    self_or_cls = re.compile(r'(?<=\()(self|cls) *\,* *')  # positive lookbehind of "(" before self|cls
    template_files = re.compile(r'\.(np)?md$')
    template_files_insensitive = re.compile(template_files.pattern, flags=re.IGNORECASE)


# # Generic helpers

# +
def previous_current_next(iterable:Iterable) -> Iterable[tuple]:
    """
    Iterator that yields (previous, current, next) tuple per element.

    Returns None if the value does not make sense (i.e. previous before
    first and next after last).

    Stolen from: https://gist.github.com/mortenpi/9604377?permalink_comment_id=3180599#gistcomment-3180599

    Examples
    --------
    >>> for t in previous_current_next((1, 2, 3)):
    ...     print(t)
    (None, 1, 2)
    (1, 2, 3)
    (2, 3, None)
    """
    iterable = iter(iterable)
    prv = None
    cur = iterable.__next__()
    try:
        while True:
            nxt = iterable.__next__()
            yield (prv, cur, nxt)
            prv = cur
            cur = nxt
    except StopIteration:
        yield (prv, cur, None)


def unique(v:Iterable) -> list:
    """
    Produces a unique list from an iterable.
    This is similar to doing list(set(some_list)) but it preserves the order.

    Examples
    --------
    >>> unique(['foo', 'foo'])
    ['foo']
    """
    u = []
    for x in v:
        if x not in u:
            u.append(x)
    return u


# -

# # Helper for file operations

class FileOperations:
    """
    Collection of methods for operations relative to files and folders
    e.g. `FileOperations.list_files`.
    """

    def _list_files_recursive(folder:str, pattern:re.Pattern) -> List[str]:
        """
        Lists files whose name match `pattern` in a folder and its subfolders
        """
        filepaths = []
        for root, dirs, files in os.walk(folder):
            for f in files:
                # search pattern inside of file name
                if pattern.search(Path(f).name):
                    fullpath = os.path.join(root, f)
                    filepaths.append(fullpath)
        return filepaths

    def _list_files_non_recursive(folder:str, pattern:re.Pattern) -> List[str]:
        """
        Lists files whose name match `pattern` in a folder but **not** in its subfolders
        """
        return [os.path.join(folder, f) for f in os.listdir(folder)
                if pattern.search(Path(f).name)]

    def list_files(folder:str, pattern:re.Pattern, recursive:bool=True) -> List[str]:
        """
        Lists files whose name match `pattern` in a `folder` and optionally in its subfolders
        (when `recursive=True`)
        """
        if recursive:
            f = FileOperations._list_files_recursive
        else:
            f = FileOperations._list_files_non_recursive
        return f(folder=folder, pattern=pattern)

    def switch_folder(source_folder:str, destination_folder:str,
                      filepath:str, create_missing_dirs:bool=True) -> str:
        """
        Switches the folder where a file is located.

        It will reproduce the folder structure of `source_folder`
        in `destination_folder`.

        Examples
        --------
        >>> FileOperations.switch_folder('D:/', 'C:/Test', filepath='D:/Subfolder/foo.md', create_missing_dirs=False) # doctest: +SKIP
        'C:/Test/Subfolder/foo.md'
        """
        relpath = os.path.relpath(filepath, source_folder)
        destination_path = os.path.join(destination_folder, relpath)
        if create_missing_dirs:
            destination_folder = Path(destination_path).parent
            destination_folder.mkdir(parents=True, exist_ok=True)
        return destination_path
