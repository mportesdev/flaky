import os.path


class InvalidModulePath(Exception):
    pass


def get_module_qualname_from_path(path):
    """Get the module's qualified name by analysis of the path.

    Resolve the absolute pathname and eliminate symlinks. This could result in
    an incorrect name if symlinks are used to restructure the python lib
    directory.

    Starting from the right-most directory component look for __init__.py in
    the directory component. If it exists then the directory name is part of
    the module name. Move left to the subsequent directory components until a
    directory is found without __init__.py.

    :param: Path to module file. Relative paths will be resolved relative to
            current working directory.
    :return: fully qualified module name
    """

    (head, tail) = os.path.split(path)
    if head == "" or tail == "":
        raise InvalidModulePath(
            'Invalid python file path: "%s"'
            " Missing path or file name" % (path)
        )

    qname = [os.path.splitext(tail)[0]]
    while head not in ["/", ".", ""]:
        if os.path.isfile(os.path.join(head, "__init__.py")):
            (head, tail) = os.path.split(head)
            qname.insert(0, tail)
        else:
            break

    qualname = ".".join(qname)
    return qualname
