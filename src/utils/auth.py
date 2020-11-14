import os


__data = {}


def __read_file(filename):
    with open(filename, 'r') as fp:
        text = fp.read()
    return text


def reload(*files):
    __data.clear()
    files = files or os.listdir('../auth')

    for filename in files:
        if filename.endswith('.txt'):
            __data[filename.rsplit(".", 1)[0]] = __read_file(filename)


def __getitem__(key):
    return __data.get(key)


reload()

