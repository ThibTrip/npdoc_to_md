# +
import re
from itertools import chain

# regex to remove console python marks
RE_CONSOLE_PY = re.compile('\>\>\> ?|\.\.\. ?')


# -

# # ExampleParser

class ExampleParser():
    """
    Formats examples in a numpy style docstring to markdown.
    Examples outputs are formatted in the language defined
    with the parameter "examples_md_flavor" (by default python).

    If any example contains a placeholder (must be before the first
    line of an example) indicating the markdown language e.g. "{{python}}"
    (see Examples of method ExampleParser.to_md_lines) then this
    overrides the parameter "examples_md_flavor".

    Parameters
    ----------
    lines : list or str
    examples_md_flavor : str, default "python"
        Which markdown language to use for example outputs.
        E.g.: ```python ...```
        There is a special flag "raw" for flavorless code
        markdown (``` ... ```).

    Examples
    --------
    >>> ex = ExampleParser(lines=['* first example',
    ...                           '{{markdown}}', # language for output
    ...                           '>>> import pandas as pd',
    ...                           '>>> df = pd.DataFrame({"A":[0, 1]})',
    ...                           '>>> df.to_markdown()',
    ...                           '|    |   A |',
    ...                           '|---:|----:|',
    ...                           '|  0 |   0 |',
    ...                           '|  1 |   1 |',
    ...                           '',
    ...                           '* second example', 
    ...                           '>>> 2+2',
    ...                           '4']) # no language for output provided -> defaults to python
    """
    def __init__(self, lines, examples_md_flavor:str='python'):
        if isinstance(lines, str):
            lines = lines.splitlines()
        elif not isinstance(lines, list):
            raise TypeError('lines must be a list or a str')
        self.lines = [l.strip() for l in lines]
        self.examples_md_flavor = examples_md_flavor

    @classmethod
    def is_flavor_placeholder(cls, line) -> bool:
        """
        Detects whether a line contains a custom placholder
        to indicate the type of output in the Examples section
        of a docstring. E.g. "{{markdown}}" for markdown outputs
        (a table for instance) or "{{python}}" or "{{raw}}"
        for flavorless code markdown (e.g. ```mycode```).

        Parameters
        ----------
        line : str

        Examples
        --------
        >>> ExampleParser.is_flavor_placeholder("{{markdown}}")
        True
        >>> ExampleParser.is_flavor_placeholder("{markdown}")
        False
        """
        return line.startswith('{{') and line.endswith('}}')

    @classmethod
    def is_python_example(cls, line):
        """
        Detects whether a line contains python example code
        by looking for ">>>" or "..." at line start.

        Parameters
        ----------
        line : str

        Examples
        --------
        >>> ExampleParser.is_python_example(">>> import pandas as pd")
        True
        >>> ExampleParser.is_python_example("... except ValueError as e")
        True
        """
        return line.startswith('>>>') or line.startswith('...')

    @classmethod
    def is_beginning_of_example(cls, line, previous_line=None):
        """
        Detects whether a line is the start of a python example code.

        See Also
        --------
        ExampleParser.is_end_of_example

        Parameters
        ----------
        line : str
        previous_line : str or None, default None
            Should be None if the example section starts with :line:
            in which case if it is python code we are necessarily at the
            beginning of a python example.

        Examples
        --------
        >>> ExampleParser.is_beginning_of_example(line=">>> import pandas as pd",
        ...                                       previous_line=None)
        True
        >>> ExampleParser.is_beginning_of_example(line=">>> import pandas as pd",
        ...                                       previous_line=">>> import numpy as np")
        False
        """
        if previous_line is None:
            return ExampleParser.is_python_example(line)
        return (ExampleParser.is_python_example(line)
                and not ExampleParser.is_python_example(previous_line))

    @classmethod
    def is_end_of_example(cls, line, next_line=None):
        """
        Detects whether a line is the end of a python example code.

        See Also
        --------
        ExampleParser.is_beginning_of_example

        Parameters
        ----------
        line : str
        next_line : str or None, default None
            Should be None if the example section ends with :line:
            in which case if it is python code we are necessarily at the
            end of a python example.

        Examples
        --------
        >>> ExampleParser.is_end_of_example(line=">>> import pandas as pd",
        ...                                 next_line=None)
        True
        >>> ExampleParser.is_end_of_example(line=">>> import pandas as pd",
        ...                                 next_line=">>> import numpy as np")
        False
        """
        if next_line is None:
            return ExampleParser.is_python_example(line)
        return (ExampleParser.is_python_example(line)
                and not ExampleParser.is_python_example(next_line))

    @classmethod
    def is_beginning_of_example_output(cls, line, previous_line=None):
        """
        Detects whether a line is the beginning of the output of a python example code.

        Parameters
        ----------
        line : str
        next_line : str or None, default None
            None if we are at the end of the example.

        Examples
        --------
        >>> ExampleParser.is_beginning_of_example_output(line="4",
        ...                                              previous_line=">>> 2+2")
        True
        >>> ExampleParser.is_beginning_of_example_output(line=">>> import numpy as np",
        ...                                              previous_line=">>> import pandas as pd")
        False
        """
        return (ExampleParser.is_python_example(previous_line)
                and not ExampleParser.is_python_example(line))

    def _get_example_outputs(self, verbose=False) -> dict:
        """
        Finds all the python example code outputs in the lines
        provided at class instantiation and which markdown flavor/
        language (see docstring of ExampleParser) to use for
        those example outputs (markdown, raw, python...).

        Parameters
        ----------
        verbose : bool, default False
            If True prints information as the function runs such
            as the indices of where outputs begin or end.

        Returns
        -------
        outputs : {range:str}
            * keys: ranges of the outputs (e.g. from line 5 to 8).
            * values: markdown flavor/language for the outputs

        Examples
        --------
        >>> ex = ExampleParser(lines=['* first example',
        ...                           '{{markdown}}', # language for output
        ...                           '>>> import pandas as pd',
        ...                           '>>> df = pd.DataFrame({"A":[0, 1]})',
        ...                           '>>> df.to_markdown()',
        ...                           '|    |   A |',
        ...                           '|---:|----:|',
        ...                           '|  0 |   0 |',
        ...                           '|  1 |   1 |',
        ...                           '',
        ...                           '* second example', 
        ...                           '>>> 2+2',
        ...                           '4']) # no language for output provided -> defaults to python                     
        >>> ex._get_example_outputs(verbose=False)
        {range(5, 9): 'markdown', range(12, 13): 'python'}
        """
        lines = self.lines

        # FIND BEGINNING OF OUPUTS AND THEIR FLAVORS (```markdown, ```python, etc.)
        outputs_begins = []
        outputs_flavors = []
        for ix, line in enumerate(lines):
            # can't have the beginning of an output at the top of the examples
            if ix ==0:
                continue
            previous_line = lines[ix-1]
            if ExampleParser.is_beginning_of_example_output(line, previous_line):
                outputs_begins.append(ix)
                # try to find the flavor of the output example
                # set default flavor in case for loop stops iteration with no match
                # e.g. the example is at the top of the Examples section
                flavor = self.examples_md_flavor # set default flavor
                for l in reversed(lines[0:ix-1]):
                    # stop when the line is not a python example
                    if not ExampleParser.is_python_example(l):
                        if ExampleParser.is_flavor_placeholder(l):
                            flavor = l.strip('{').strip('}') # overwrite default flavor
                        break
                outputs_flavors.append(flavor)
        # make sure we have as much flavors as begin indices
        assert len(outputs_flavors) == len(outputs_begins)
        if verbose:
            print(f'Indices of output begins: {outputs_begins}')
            print(f'Flavors of ouputs {outputs_flavors}')
        # FIND END OF OUTPUTS
        outputs_ends = []
        for ix in outputs_begins:
            end_ix = ix
            for l in lines[ix:]:
                # search next empty line or next python example (they may not be separated)
                if l.strip() == '' or ExampleParser.is_python_example(l):
                    break
                end_ix +=1
            outputs_ends.append(end_ix)
        # make sure we have as much as begin indices as end indices
        assert len(outputs_begins) == len(outputs_ends)
        if verbose:
            print(f'Indices of output ends: {outputs_ends}')
        # zip begin and ends to make ranges
        # then zip ranges and flavors
        outputs = tuple(zip(outputs_begins, outputs_ends))
        outputs = tuple([(range(a,b)) for a,b in outputs])
        outputs = dict(zip(outputs,outputs_flavors))
        return outputs

    def to_md_lines(self, remove_doctest_blanklines=True):
        """
        Converts the lines provided at class instantiation
        to markdown lines.

        Examples
        --------
        >>> from pprint import pprint
        >>> 
        >>> ex = ExampleParser(lines=['* first example',
        ...                           '{{markdown}}', # language for output
        ...                           '>>> import pandas as pd',
        ...                           '>>> df = pd.DataFrame({"A":[0, 1]})',
        ...                           '>>> df.to_markdown()',
        ...                           '|    |   A |',
        ...                           '|---:|----:|',
        ...                           '|  0 |   0 |',
        ...                           '|  1 |   1 |',
        ...                           '',
        ...                           '* second example', 
        ...                           '>>> 2+2',
        ...                           '4']) # no language for output provided -> defaults to python
        >>> 
        >>> # Notice in the results below that before the table there is no block identifier such as ```
        >>> # because the table is in markdown syntax
        >>> pprint(ex.to_md_lines())
        ['* first example',
         '```python',
         'import pandas as pd',
         'df = pd.DataFrame({"A":[0, 1]})',
         'df.to_markdown()',
         '```',
         '|    |   A |',
         '|---:|----:|',
         '|  0 |   0 |',
         '|  1 |   1 |',
         '',
         '* second example',
         '```python',
         '2+2',
         '```',
         '```python',
         '4',
         '```']
        """
        lines = self.lines
        md_example_section = []
        outputs = self._get_example_outputs()

        def get_flavor_of_output(line_index):
            """
            Gets the markdown flavor/language for the given line index
            located in a python example output e.g. "```python".
            """
            # go through the outputs, then their ranges (keys of the outputs dict)
            # and check if line_index is in given range
            for range_, flavor in outputs.items():
                if line_index in range_:
                    return flavor
            raise ValueError(f'index {line_index} does not seem to be an output')

        def is_beginning_of_output(line_index):
            """
            Checks if given line index corresponds to the beginning of a python
            example output.
            """
            for range_, flavor in outputs.items():
                if line_index in range_ and line_index == list(range_)[0]:
                    return True
            return False
    
        def is_end_of_output(line_index):
            """
            Checks if given line index corresponds to the end of a python
            example output.
            """
            # go through the outputs, then their ranges (keys of the outputs dict)
            # and check if line_index is the last index in given range 
            for range_, flavor in outputs.items():
                if line_index in range_ and line_index == list(range_)[-1]:
                    return True
            return False

        # go over the lines and compare previous and next lines when available
        for ix, line in enumerate(lines):
            previous_line = lines[ix-1] if ix != 0 else None
            next_line = lines[ix+1] if ix < len(lines) - 1 else None

            # THINGS TO PREPEND TO GIVEN LINE
            # if we are at the beginning of a python example code
            # we need to add "```python" (markdown syntax for python code block)
            # before the example (and we'll have to end with "```" later)
            if ExampleParser.is_beginning_of_example(line, previous_line):
                md_example_section.append('```python')
            # if we are at the beginining of an output add the output flavor (e.g. python)
            # or nothing in the case of markdown
            elif is_beginning_of_output(ix):
                flavor = get_flavor_of_output(ix)
                # handle special flag "raw" for flavorless markdown code (```...```)
                flavor = '' if flavor == 'raw' else flavor
                if flavor != 'markdown':
                    md_example_section.append(f'```{flavor}')

            # ADD LINE
            # skip flavor placeholders
            if not ExampleParser.is_flavor_placeholder(line):
                # add line (remove ">>>" and "..." if a Python example)
                if ExampleParser.is_python_example(line):
                    md_example_section.append(RE_CONSOLE_PY.sub('',line))
                else:
                    md_example_section.append(line)

            # THINGS TO APPEND TO GIVEN LINE
            # close end of python example codes with ```
            if ExampleParser.is_end_of_example(line, next_line):
                md_example_section.append('```')
            # close end of python example code outputs with ```
            # if the flavor is not markdown
            elif is_end_of_output(ix):
                flavor = get_flavor_of_output(ix)
                if flavor != 'markdown':
                    md_example_section.append('```')

        # remove <BLANKLINE> used for doctest if so desired
        # do this here to not break the logic above since we compare
        # each line with its previous and next line
        if remove_doctest_blanklines:
            md_example_section = ['' if l == '<BLANKLINE>' else l for l in md_example_section]
        return md_example_section


# # Function to convert numpydoc sections to markdown

def numpydoc_section_to_md_lines(numpydoc_obj, section_name, 
                                 examples_md_flavor='python',
                                 md_section_level='####',
                                 remove_doctest_blanklines=True):
    """
    Converts a section of a numpydoc object (see Parameters)
    to lines of markdown strings.

    Parameters
    ----------
    numpydoc_obj : numpydoc.docscrape.FunctionDoc or numpydoc.docscrape.ClassDoc
        FunctionDoc also works for class methods.
    section_name : {'Signature', 'Summary', 'Extended Summary', 'Parameters', 'Returns',
                    'Yields', 'Receives', 'Raises', 'Warns', 'Other Parameters',
                    'Attributes', 'Methods', 'See Also', 'Notes', 'Warnings',
                    'References', 'Examples', 'index'}
        See https://numpydoc.readthedocs.io/en/latest/format.html
    examples_md_flavor : str
        Only relevant for the Examples section.
        Gives instruction on how to format python example codes outputs.
        E.g. "markdown" if you have tables or "python" (```python)
        if the output is a list or "raw" for flavorless markdown
        code block (```).

    Warnings
    --------
    We don't deal with the "Signature" section because in the functions
    we expose to the end user (see npdoc_to_md.core module) we use inspect
    to fetch the object signature and it gives us more information and flexibility.

    Examples
    --------
    >>> from pprint import pprint
    >>> from numpydoc.docscrape import FunctionDoc
    >>> from npdoc_to_md.testing import example_func
    >>> 
    >>> # parse numpy docstring
    >>> numpydoc_obj = FunctionDoc(example_func)
    >>> 
    >>> pprint(numpydoc_section_to_md_lines(numpydoc_obj, section_name='Summary'))
    ['Example function that sums to integers.', '', '']

    >>> pprint(numpydoc_section_to_md_lines(numpydoc_obj, section_name='Parameters'))
    ['#### Parameters',
     '* a : <b><i>int</i></b>  First number.',
     '\\tMultiline test.',
     '* b : <b><i>int</i></b> ',
     '']

    >>> pprint(numpydoc_section_to_md_lines(numpydoc_obj, section_name='See Also'))
    ['#### See Also',
     '* example_func2, example_func3 : Other useless functions.',
     'Multiline test.',
     '']

    >>> pprint(numpydoc_section_to_md_lines(numpydoc_obj, section_name='Examples'))
    ['#### Examples',
     '* fist example',
     '```python',
     'example_func(1, 1)',
     '```',
     '```python',
     '2',
     '```',
     '',
     '* second example',
     '```python',
     'example_func(2, 2)',
     '```',
     '```python',
     '4',
     '```',
     '',
     '* third example (test markdown)',
     '```python',
     'import pandas as pd',
     "df = pd.DataFrame({'A':[1, 2]})",
     'print(df.to_markdown())',
     '```',
     '|    |   A |',
     '|---:|----:|',
     '|  0 |   1 |',
     '|  1 |   2 |',
     '',
     '* fourth example (raw code block)',
     '```python',
     "print('Hello world!')",
     '```',
     '```',
     'Hello world!',
     '```',
     '']
    """
    # get section
    # it may be a list or a numpydoc obj
    section = numpydoc_obj[section_name]
    # disgard empty sections 
    if section in ([],[''],''):
        return []

    # CREATE HEADER
    # start with a header except for summary and extended summary
    lines = [f'{md_section_level} {section_name}'] if section_name not in ('Summary', 'Extended Summary') else []

    # CREATE BODY
    if section_name in ('Summary', 'Extended Summary', 'Warnings', 'Notes', 'References'):
        lines.extend([l+'\n' for l in section])
        # add a separation line between Summary and Extended Summary
        if section_name == 'Summary':
            lines.append('')

    # cases where we have listings like parameters
    elif section_name in ('Returns', 'Yields', 'Parameters', 'Attributes',
                          'Raises', 'Warns', 'Receives', 'Other Parameters'):
        for item in section:
            # parsed section looks like this:
            # [Parameter(name='number_plus_one', type='int', desc=['Your number plus one :)'])]
            name = f"* {item.name}" if item.name != '' else ''
            type_ = f"<b><i>{item.type}</i></b> " if item.type != '' else ''
            description = []
            for ix, l in enumerate(item.desc):
                new_l = '\t' + l if ix != 0 else l
                description.append(new_l)
            description = '\n'.join(description)
            # separator between name and type
            sep0 = ' : ' if name != '' else ''
            # separator between type_ and description
            sep1 = ' ' if description != '' else ''
            lines.append(f"{name}{sep0}{type_}{sep1}{description}")

    # special case "See Also" section
    # It will test if the function truly exist (within the module or globally if the full
    # namespace is provided)
    elif section_name == 'See Also':
        for funcs, description in section:
            # example of (funcs, description):
            # ([('example_func2', None), ('example_func3', None)], ['description'])
            # not sure what None could be (second item of each tuple in funcs) ?!
            names = ', '.join(func[0] for func in funcs)
            description = '\n'.join(description)
            sep = ' : ' if description != '' else ''
            lines.append(f"* {names}{sep}{description}")

    # very special case "Examples" section
    elif section_name == 'Examples':
        ex = ExampleParser(lines=section, examples_md_flavor=examples_md_flavor)
        lines.extend(ex.to_md_lines(remove_doctest_blanklines=remove_doctest_blanklines))

    # FINALIZE
    # add an empty line at the end of the section
    lines.append('') 
    # instead of \n use a blank line ['test.\n'] into ['test', '']
    # this will make it easier for doctest and is simply more coherent
    # since both techniques for making new lines are used above
    splitted = [v.splitlines() for v in lines]
    splitted = [[''] if v == [] else v for v in splitted]
    lines = list(chain.from_iterable(splitted))
    return lines
