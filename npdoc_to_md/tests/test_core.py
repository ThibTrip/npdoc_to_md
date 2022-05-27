# +
"""
Tests the core module. Basically end to end tests.
"""
import os
import pytest
import tempfile
from dataclasses import dataclass
from typing import Any, List, Optional

# local imports
from npdoc_to_md.core import RenderedFile, render_obj_docstring, render_string, render_file, render_folder
from npdoc_to_md.config import MemberFlag
from npdoc_to_md.tests.conftest import CLIRunner, CustomNamedTemporaryFile
from npdoc_to_md.tests.expectations import (builtins_none_md,
                                            documented_func_example_md,
                                            documented_generator_func_example_md,
                                            DocumentedClassExampleMd,
                                            empty_function_md,
                                            EmptyClassMd,
                                            EmptyClassDictMd,
                                            empty_doc_sections_function_md,
                                            EmptyDocSectionsClass_md,
                                            none_md,
                                            testing_module_md,
                                            RENDERING_OPTIONS)


# -

# # Helpers

# ## Generating placeholders

class PlaceholderStringGenerator:
    """
    Creates a placeholder string (e.g. for putting into a template file)
    from given placeholder parameters.

    Examples
    --------
    >>> PlaceholderStringGenerator.generate(obj="pandas.DataFrame",
    ...                                     alias="pd.DataFrame",
    ...                                     examples_md_lang='raw',
    ...                                     remove_doctest_skip=True,
    ...                                     remove_doctest_blanklines=True,
    ...                                     md_section_level=3,
    ...                                     ignore_custom_section_warning=True,
    ...                                     members=['public$', '+__dict__', '-to_dict'])  # doctest: +SKIP
    "{{'obj':'pandas.DataFrame', 'alias':'pd.DataFrame', 'examples_md_lang':'raw', 'remove_doctest_skip':true, \
'remove_doctest_blanklines':true, 'md_section_level':'3', 'ignore_custom_section_warning':true, \
'members':['public$', '+__dict__', '-to_dict']}}"
    """

    def _format_value(param_name:str, param_value:Any):
        if param_name in ('remove_doctest_blanklines', 'remove_doctest_skip', 'ignore_custom_section_warning'):
            assert isinstance(param_value, bool)
            return str(param_value).lower()  # true, false

        elif param_name == 'members':
            assert isinstance(param_value, list)
            return '[' + ','.join(f'"{s}"' for s in param_value) + ']'

        else:
            return f'"{param_value}"'

    def generate(**placeholder_params):
        args = []
        for k, v in placeholder_params.items():
            v = PlaceholderStringGenerator._format_value(param_name=k, param_value=v)
            args.append(f'"{k}":{v}')
        return '{{' + ','.join(args) + '}}'


# ## "Flexible" tester for pytest

@dataclass(frozen=True)
class PytestTester:
    """
    Tool for testing the rendering of the docstring of a Python object
    using the various functions of the library in Python and in the CLI:
    * `render_obj_docstring`: we can pass the object (actually its namespace) directy to this function
    * `render_string`: we will pass the object  (actually its namespace) through a placeholder
    * `render_file`: we will create a temporary file with only a placeholder pointing to
      the object
    * `render_folder`: we will create a temporary directory and there add a file with only
      a placeholder pointing to the object

    Notes
    -----
    This could probably by DRYer...

    Parameters
    ----------
    obj_namespace
        Importable string e.g. "pandas.DataFrame".
        In `render_obj_docstring` as in placeholders this is referred to as parameter `obj`
    expected
        Expected Markdown string after rendering the docstring
    rendering_options
        See options in docstring of `render_obj_docstring`
    use_cli
        If False uses Python otherwise uses the CLI
    hyphenize
        Only relevant for the CLI. If True underscores are converted to hyphens.
        This is for testing whether underscores and hyphens can be switched
        in commands and parameters
    """
    obj_namespace:str
    expected:str
    rendering_options:dict
    use_cli:bool
    hyphenize:bool

    def _run_in_cli(self, func, kwargs, extras:Optional[List[str]]=None):
        extras = [] if extras is None else extras
        result = CLIRunner(func=func, kwargs=kwargs, command=['npdoc_to_md', func.__name__],
                           hyphenize=self.hyphenize).run(extras=extras).strip()
        # IMPORANT! The line below will normalize line breaks to \n (in Windows it would be \r\n)
        return '\n'.join(result.splitlines())

    def using_obj(self):
        # prepare function and params
        func = render_obj_docstring
        kwargs = self.rendering_options.copy()
        if self.use_cli:
            # we need to escape None for the CLI otherwise it will be interpreted as
            # a None instead of the string "None"
            if self.obj_namespace == 'None':
                kwargs['obj'] = "'None'"
            else:
                kwargs['obj'] = self.obj_namespace
            if 'members' in kwargs:
                kwargs['members'] = str(kwargs['members'])
        else:
            kwargs['obj'] = self.obj_namespace

        # get and check result
        result = self._run_in_cli(func=func, kwargs=kwargs) if self.use_cli else func(**kwargs)
        assert result == self.expected

    def using_string(self):
        # prepare function and params
        func = render_string
        placeholder_string = PlaceholderStringGenerator.generate(obj=self.obj_namespace, **self.rendering_options)

        # get result
        # for testing the function "npdoc_to_md.render_string" with the CLI
        # we do a little "hack" where we prepend a dummy line
        # to avoid awkward escaping (multiline strings are treated differently)...
        if self.use_cli:
            string = f'Demo:\n{placeholder_string}'
            expected = f'Demo:\n{self.expected}'
            result = self._run_in_cli(func=func, kwargs={'string':string})
        else:
            result = func(string=placeholder_string)
            expected = self.expected
        assert result == expected

    def using_file(self):
        # preparations
        func = render_file
        placeholder_string = PlaceholderStringGenerator.generate(obj=self.obj_namespace, **self.rendering_options)

        # work in temp files
        with CustomNamedTemporaryFile() as input_tmp, CustomNamedTemporaryFile() as output_tmp:

            # write input file
            source = input_tmp.name + '.npmd'
            destination = output_tmp.name + '.md'
            with open(source, mode='w', encoding='utf-8', newline='\n') as fh:
                fh.write(placeholder_string)

            # get result
            kwargs = dict(source=source, destination=destination)
            if self.use_cli:
                # the extras will allow us to access the property "rendered_text"
                # of the class RenderedFileCLI (the python-fire library we use for the CLI has such features)
                result = self._run_in_cli(func=func, kwargs=kwargs, extras=['-', 'rendered_text'])
            else:
                rendered_file:RenderedFile = func(**kwargs)
                result = rendered_file.rendered_text
            assert result == self.expected

            # check output file as well
            with open(destination, mode='r', encoding='utf-8', newline='\n') as fh:
                file_result = fh.read()
            assert file_result == self.expected

    def using_folder(self):
        # preparations
        func = render_folder
        placeholder_string = PlaceholderStringGenerator.generate(obj=self.obj_namespace, **self.rendering_options)

        # work in temp dir
        with tempfile.TemporaryDirectory() as inputdirpath, tempfile.TemporaryDirectory() as outputdirpath:

            # write a test file
            test_filepath = os.path.join(inputdirpath, 'Test.npmd')
            with open(test_filepath, mode='w', encoding='utf-8', newline='\n') as fh:
                fh.write(placeholder_string)

            # get result
            kwargs = dict(source=inputdirpath, destination=outputdirpath)
            if self.use_cli:
                # the extras will allow us to access the property "rendered_text" of the first item
                # (an instance of the class RenderedFileCLI)
                result = self._run_in_cli(func=func, kwargs=kwargs, extras=['-', '0', '-', 'rendered_text'])
            else:
                rendered_files:List[RenderedFile] = func(**kwargs)
                result = rendered_files[0].rendered_text
            assert result == self.expected

            # check output file as well
            test_filepath_converted = os.path.join(outputdirpath, 'Test.md')
            with open(test_filepath_converted, mode='r', encoding='utf-8', newline='\n') as fh:
                file_result = fh.read()
            assert file_result == self.expected


# ## Expectations as parameters for pytest

# [(obj_namespace, expected_rendered_docstring)]
doc_expectations = [('npdoc_to_md.testing.documented_func_example', documented_func_example_md),
                    ('npdoc_to_md.testing.documented_generator_func_example', documented_generator_func_example_md),
                    ('npdoc_to_md.testing.DocumentedClassExample', DocumentedClassExampleMd),
                    ('npdoc_to_md.testing', testing_module_md),
                    # objects with empty docstrings or sections
                    ('npdoc_to_md.testing.empty_function', empty_function_md),
                    ('npdoc_to_md.testing.EmptyClass', EmptyClassMd),
                    ('npdoc_to_md.testing.EmptyClass.__dict__', EmptyClassDictMd),
                    ('npdoc_to_md.testing.empty_doc_sections_function', empty_doc_sections_function_md),
                    ('npdoc_to_md.testing.EmptyDocSectionsClass', EmptyDocSectionsClass_md),
                    ('None', none_md),
                    ('builtins.None', builtins_none_md)]


# # Test expectations of rendering for our tests functions

@pytest.mark.parametrize('test_method', [m for m in dir(PytestTester) if m.startswith('using_')])
@pytest.mark.parametrize('runner', ['cli_underscore', 'cli_hyphen', 'python'])
@pytest.mark.parametrize('obj_namespace, expected', doc_expectations,
                         # don't show the long docstrings in the pytests ids
                         ids=[item[0] for item in doc_expectations])
def test_render_docstring(test_method, runner, obj_namespace, expected):

    # handle special case where we want to test the rendering of the docstrings of class members
    rendering_options = RENDERING_OPTIONS.copy()
    if obj_namespace == 'npdoc_to_md.testing.DocumentedClassExample':
        rendering_options['members'] = [MemberFlag.PUBLIC.value]

    pt = PytestTester(obj_namespace=obj_namespace, expected=expected, rendering_options=rendering_options,
                      use_cli=runner.startswith('cli'), hyphenize=runner.endswith('hyphen'))
    getattr(pt, test_method)()
