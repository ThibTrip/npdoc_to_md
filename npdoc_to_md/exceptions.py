# +
"""
Custom exceptions for the library
"""


class NonExistentObjectException(Exception):
    pass


class SignatureNotFoundException(Exception):
    pass


class NonExistentMemberException(Exception):
    pass


class MembersConflictsException(Exception):
    pass


class InvalidMembersFlagException(Exception):
    pass
