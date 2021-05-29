import re

regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'


def any_empty(*args):
    for s in args:
        if s == '':
            return True
    return False


def correct_email(email):
    return re.search(email, regex)


def more_than(*args, length):
    for s in args:
        if len(s) < length:
            return False
    return True
