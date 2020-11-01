# +
import os
import argparse
from pkg_resources import resource_filename

script_description = """
This script generates the documentation of the library npdoc_to_md using its own functions
to render markdown files (located in the same folder as this script) with Jinja like placeholders (docstrings of functions,
methods or classes are pulled and converted to pretty markdown).

It takes a single argument which is the path to npdoc_to_md's wiki which you must have
cloned on your computer (git clone https://github.com/ThibTrip/npdoc_to_md.wiki.git).

To use the script, replace "NPDOC_TO_MD_PATH" with the path to the cloned repo of npdoc_to_md
and replace "WIKI_FOLDER_PATH" with the path to the cloned wiki folder. Then, assuming you are
in the same folder as the script you can run this command:

$ python generate_documentation.py NPDOC_TO_MD_PATH WIKI_FOLDER_PATH
"""


# -

# # Parse arguments

def parse_arguments():
    parser = argparse.ArgumentParser(description=script_description)
    parser.add_argument('npdoc_to_md_path', metavar='wiki_path', type=str, help="Path to npdoc_to_md' cloned repo folder on your computer")
    parser.add_argument('wiki_path', metavar='wiki_path', type=str, help="Path to npdoc_to_md' cloned wiki folder on your computer")
    args = parser.parse_args()
    npdoc_to_md_path = args.npdoc_to_md_path
    wiki_path = args.wiki_path
    return npdoc_to_md_path, wiki_path


# # Render markdown files
#
# Each Markdown file corresponds to a wiki page except README.md

# +
def generate_doc(npdoc_to_md_path, wiki_path):
    from npdoc_to_md import render_md_file, get_markdown_files_in_dir

    script_dir = resource_filename('npdoc_to_md.docs.generate_documentation', '')
    files_and_names = get_markdown_files_in_dir(script_dir)

    # simple verification that the page "Home" is present
    has_home_md = any(['home.md' in v.lower() for v in files_and_names.values()])
    if not has_home_md:
        raise AssertionError('Expected a Home.md page (case insensitive match) '
                             'and did not find any. The script searched for '
                             f'markdown files in the path "{script_dir}"')

    # render Markdowns
    for file, name in files_and_names.items():
        # render the file and put it in the correct destination (npdoc_to_md root folder for the README file
        # and the wiki for other files)
        if name == 'README.md':
            destination = os.path.join(npdoc_to_md_path, name)
        else: 
            destination = os.path.join(wiki_path, name)
        print(f'Rendering and saving file "{file}" to path "{destination}"')
        render_md_file(source=file, destination=destination)
    print('Done')

if __name__ == '__main__':
    npdoc_to_md_path, wiki_path = parse_arguments()
    generate_doc(npdoc_to_md_path, wiki_path)
