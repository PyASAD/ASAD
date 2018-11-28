#!/usr/bin/env python
import os
import shutil

try:
    import asad.args as args

    if __name__ == '__main__':
        args.init()
except Exception as err:
    print('\n\t Deleting caches before stopping...\n\n')
    if os.name == 'nt':
        working_path = os.getcwd()
        working_path = working_path + '\\' + 'data' + '\\' + 'temp'
        caches = os.listdir(working_path)
        for f in caches:
            try:
                os.remove(working_path + '\\' + f)
            except Exception:
                shutil.rmtree(working_path + '\\' + f)
            pass
    elif os.name == 'mac' or os.name == 'posix':
        working_path = os.getcwd()
        working_path = working_path + '/' + 'data' + '/' + 'temp'
        caches = os.listdir(working_path)
        for f in caches:
            try:
                os.remove(working_path + '/' + f)
            except Exception:
                shutil.rmtree(working_path + '/' + f)
    raise(err)
