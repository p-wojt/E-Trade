import re

regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
cryptocurrency_buttons = ['buy_bitcoin', 'sell_bitcoin', 'buy_litecoin', 'sell_litecoin', 'buy_ethereum',
                          'sell_ethereum', 'buy_dogecoin', 'sell_dogecoin']


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


def check_buysell_buttons(req):
    for i in cryptocurrency_buttons:
        if i in req:
            return i
    return None
