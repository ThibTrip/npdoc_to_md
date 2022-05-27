"""
Tests the sections module
"""
import pytest
from npdoc_to_md.sections import SectionsFinder


# # Tests

# I am putting the lines on top of each other in the tuples on purpose
# so we can see them better, sorry for the ugly display
@pytest.mark.parametrize('line, next_line, expected', [('My Section',  # "normal" case
                                                        '----------',
                                                        'My Section'),
                                                       # with leading spaces (should still work)
                                                       ('  My Section',
                                                        '  ----------',
                                                        'My Section'),
                                                       # not enough hyphens (for this test,
                                                       # the length of both lines must match
                                                       # after being rstripped)
                                                       ('My Section',
                                                        ' ---------',
                                                        None),
                                                       # too many hyphens
                                                       (' My Section',
                                                        '-----------',
                                                        None),
                                                       # something that looks like a section
                                                       # but is not one
                                                       ('  Not a section',
                                                        '  -----foo-----',
                                                        None)])
def test_finding_sections_from_lines(line, next_line, expected):
    assert SectionsFinder._find_from_lines(line=line, next_line=next_line) == expected
