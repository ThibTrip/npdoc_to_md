# +
"""
Labels lines of docstrings (right now used for examples
to distinguish between lines of inputs/ouputs or "text"
lines outside of examples)
"""
from dataclasses import dataclass
from enum import IntEnum, auto as enumauto
from typing import List, Union

# local imports
from npdoc_to_md.helpers import Patterns, previous_current_next


# -

# # Labels

class ExampleLineType(IntEnum):
    """
    Labels for lines in the example section of a docstring

    Attributes
    ----------
    INPUT : int
        Inputs found in examples (>>> or ...)
    OUTPUT : int
        Outputs of examples
    TEXT : int
        Anything before inputs that is not part of the output of a previous example
    OUTPUT_LANG : int
        Special placeholder of this library that tells us
        how to represent outputs (as markdown, python code, raw code, ...)
    """
    INPUT = enumauto()
    OUTPUT = enumauto()
    TEXT = enumauto()
    OUTPUT_LANG = enumauto()


# # Helper dataclasses

# +
@dataclass(frozen=True)
class ExampleLine:
    global_index:int
    line:str
    line_type:ExampleLineType


@dataclass(frozen=True)
class ExampleBlock:
    """
    Represents a single example block which may contain:
    * placeholders for the language of the output of the example
    * text
    * inputs
    * output

    For instance:

    {{python}}
    Some random example
    >>> a = 'foo'
    >>> a
    'foo'
    """

    example_lines:List[ExampleLine]

    @property
    def output_lang(self) -> str:
        # locate the first line indicating the language for the example output e.g. {{html}}
        iterator = (exl.line for exl in self.example_lines if exl.line_type is ExampleLineType.OUTPUT_LANG)
        flav = next(iterator, None)
        return flav.lstrip('{').rstrip('}').strip() if flav is not None else None

    def _get_ix(self, operator:Union[min, max], line_type:ExampleLineType):
        """
        Helper to make properties for notable line indices in the example block
        e.g. property `ix_first_input`.
        """
        iterator = (exl.global_index for exl in self.example_lines if exl.line_type is line_type)
        return operator(iterator, default=None)

    @property
    def ix_first_input(self) -> int:
        return self._get_ix(operator=min, line_type=ExampleLineType.INPUT)

    @property
    def ix_last_input(self) -> int:
        return self._get_ix(operator=max, line_type=ExampleLineType.INPUT)

    @property
    def ix_first_output(self) -> int:
        return self._get_ix(operator=min, line_type=ExampleLineType.OUTPUT)

    @property
    def ix_last_output(self) -> int:
        return self._get_ix(operator=max, line_type=ExampleLineType.OUTPUT)

    def __repr__(self):
        # for once we should overwrite the dataclass repr
        # this will look much better
        tab = ' ' * 4  # don't use \t otherwise this will be painful with doctest
        exl_str = '\n'.join(f'{tab}{repr(exl)}' for exl in self.example_lines)
        return f'{self.__class__.__name__}\n{exl_str}'


# -

# # Main object

@dataclass(frozen=True)
class ExamplesLabeller:
    """
    Puts a label for each line in the example section of a docstring.
    The labels distinguish inputs (>>>, ...), ouputs and any text
    that preceedes inputs.

    Examples
    --------
    >>> from pprint import pprint
    >>>
    >>> lines = ['{{python}}',
    ...          '* first example',
    ...          '>>> print(123)',
    ...          '123',
    ...          '',
    ...          '* second example',
    ...          '>>> print("hello")',
    ...          'hello']
    >>> el = ExamplesLabeller(lines=lines)
    >>> pprint(el.example_blocks)
    [ExampleBlock
        ExampleLine(global_index=0, line='{{python}}', line_type=<ExampleLineType.OUTPUT_LANG: 4>)
        ExampleLine(global_index=1, line='* first example', line_type=<ExampleLineType.TEXT: 3>)
        ExampleLine(global_index=2, line='>>> print(123)', line_type=<ExampleLineType.INPUT: 1>)
        ExampleLine(global_index=3, line='123', line_type=<ExampleLineType.OUTPUT: 2>),
     ExampleBlock
        ExampleLine(global_index=4, line='', line_type=<ExampleLineType.TEXT: 3>)
        ExampleLine(global_index=5, line='* second example', line_type=<ExampleLineType.TEXT: 3>)
        ExampleLine(global_index=6, line='>>> print("hello")', line_type=<ExampleLineType.INPUT: 1>)
        ExampleLine(global_index=7, line='hello', line_type=<ExampleLineType.OUTPUT: 2>)]

    >>> el.example_blocks[0].output_lang
    'python'

    >>> print(el.example_blocks[1].output_lang)
    None
    """
    lines:List[str]

    @property
    def labels(self):
        lines = self.lines
        if len(lines) == 0:  # pragma: no cover
            return []
        labelled_lines = []
        for ix, (previous_line, line, current_line) in enumerate(previous_current_next(lines)):
            # easy case where we know it's an input
            is_input = Patterns.console_py.search(line)
            if is_input:
                labelled_lines.append(ExampleLine(global_index=ix, line=line, line_type=ExampleLineType.INPUT))
                continue

            # distinguish outputs and comments before tests
            previous_label = labelled_lines[ix - 1].line_type if ix > 0 else None
            # note that an empty line ends an example
            # indeed, in pytest you even have to use <BLANKLINE> to indicate an empty line as part of an output
            follows_input = previous_line is not None and previous_label is ExampleLineType.INPUT
            follows_output = previous_label is ExampleLineType.OUTPUT
            is_empty_line = line.strip() == ''
            previous_line_empty = previous_line is not None and previous_line.strip() == ''
            is_example_output = ((follows_input and not is_input and not is_empty_line) or
                                 (follows_output and not is_empty_line and not previous_line_empty))
            if is_example_output:
                labelled_lines.append(ExampleLine(global_index=ix, line=line, line_type=ExampleLineType.OUTPUT))
            else:
                # if not an example output we have to assume by elimination that it is some information (text)
                # before the example e.g. "* first example"
                stripped = line.strip()
                is_lang = stripped.startswith('{{') and stripped.endswith('}}')
                line_type = ExampleLineType.OUTPUT_LANG if is_lang else ExampleLineType.TEXT
                labelled_lines.append(ExampleLine(global_index=ix, line=line, line_type=line_type))
        assert len(labelled_lines) == len(self.lines)
        return labelled_lines

    @property
    def example_blocks(self):
        # find the start of each example block using the labels
        blocks_start = []
        labels = self.labels
        for ix, example_line in enumerate(labels):
            # easy case of the first example
            if ix == 0:
                blocks_start.append(ix)
                continue

            # easy case of examples separated by a line break
            previous = labels[ix - 1]
            if previous.line_type is ExampleLineType.INPUT and example_line.line.strip() == '':
                blocks_start.append(ix)
                continue

            # for the other examples wait for an output line (could also be an empty
            # line separating the examples, I have not made a distinction for that)
            # before
            # declaring a new block
            if previous.line_type is not ExampleLineType.OUTPUT:
                continue
            if example_line.line_type in (ExampleLineType.INPUT, ExampleLineType.TEXT):
                blocks_start.append(ix)

        # get the corresponding line objects
        blocks = []
        for _, start_ix, next_ix in previous_current_next(blocks_start):
            if next_ix is not None:
                blocks.append(ExampleBlock(labels[start_ix:next_ix]))
            # case of last item
            else:
                blocks.append(ExampleBlock(labels[start_ix:]))
        return blocks
