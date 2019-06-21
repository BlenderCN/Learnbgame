import re


def clean_name(name, use_re=False):
    if use_re:
        sub = re.sub(r'[_.-]', r' ', name[:-6] if name.endswith('.blend') else name).capitalize()
        if sub[0] == ' ':
            sub = sub[1:]
        if len(sub.split(' ')[0]) < 4:
            prefix = sub.split(' ')[0].upper()
            sub = '{} {}'.format(prefix, sub[len(sub.split(' ')[0]) + 1:].capitalize())
    elif name.endswith('.blend'):
        sub = name[:-6]
    else:
        sub = name

    return sub
