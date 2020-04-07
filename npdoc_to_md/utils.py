import os


# # List markdown files in a dir

def get_markdown_files_in_dir(dir_path:str) -> dict:
    """
    Lists markdown files in a folder.

    Parameters
    ----------
    dir_path : str

    Returns
    -------
    path_and_names : dict, {str:str}
        E.g. {'/home/user/README.md':'README.md'}

    Examples
    --------
    >>> files_and_names = get_markdown_files_in_dir(".") # doctest: +SKIP
    {'/home/user/README.md':'README.md'}
    """
    paths = (os.path.join(dir_path, fn) for fn in next(os.walk(dir_path))[2])
    paths = [os.path.abspath(p) for p in paths if p.lower().endswith('.md')]
    names = [os.path.split(p)[-1] for p in paths]
    assert len(paths) == len(names)
    return dict(zip(paths, names))
