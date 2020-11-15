import os


__data = {}


AUTH_FOLDER = '/auth/'


def __read_file(filename):
    with open(filename, 'r') as fp:
        text = fp.read()
    return text


def reload(*files):
    __data.clear()
    files = files or os.listdir(AUTH_FOLDER)

    for filename in files:
        if filename.endswith('.txt'):
            __data[filename.rsplit(".", 1)[0]] = __read_file(AUTH_FOLDER+filename)
        elif filename.endswith('.py'):
            __data[filename.rsplit(".", 1)[0]] = eval(__read_file(AUTH_FOLDER+filename))


def __getitem__(name):
    if name == 'reload':
        return reload

    return __data.get(name)


def __getattr__(name):
    return __data.get(name)


reload()

