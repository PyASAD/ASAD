def do_write(self, arg, prefix='', ):
    "Write current bases to a directory"
    path = parse_args(arg, expected=1)[0]
    if not os.path.isdir(path):
        if self.config['object_temp_path_ndx'] < 0:
            error_print('\nAn Error Occured!__//WRITING_ERROR 1\n')
        else:
            error_print('Must be a directory not a path: {}'.format(path))
            return None
    if self.config['object_temp_path_ndx'] == 0:
        #--------------------------
        for base in self.values:
            #print(base.name)
            tstr = time.strftime('%H_%M_%S+%d-%m-%y', time.localtime())
            fpath = os.path.join(path, prefix + '_' + tstr + '_' + self.config['temporary__string'])
            if os.path.exists(fpath):
                if self.config['object_temp_path_ndx'] < 0 and path == self.config['object_temp_path']:
                        error_print('\nAn Error Occured!__//WRITING_ERROR 2\n')
                else:
                    error_print('{} already exists, Skipping'.format(fpath))
                    raise Exception('file already exists')
            else:
                print(base.format(), file=io.open(fpath, 'w', encoding='utf-8'))
                if self.config['object_temp_path_ndx'] < 0:
                    pass
                else:
                    pass
                    try:
                        return str(prefix + '_' + tstr + '_' + self.config['temporary__string'])
                    except:
                        error_print('@')
                    ok_print('Wrote {} to path: {}'.format(self.config['temporary__string'], fpath))

    else:
        for base in self.values:
            #print(base.name)
            tstr = time.strftime('%H_%M_%S+%d-%m-%y', time.localtime())
            fpath = os.path.join(path, prefix + '_' + tstr + '_' + base.name)
            if os.path.exists(fpath):
                if self.config['object_temp_path_ndx'] < 0:
                        error_print('\nAn Error Occured!__//WRITING_ERROR 2\n')
                else:
                    error_print('{} already exists, Skipping'.format(fpath))
                    raise Exception('file already exists')
            else:
                print(base.format(), file=io.open(fpath, 'w'))
                if self.config['object_temp_path_ndx'] < 0:
                    pass
                    #print(prefix + '_' + tstr + '_' + base.name)
                    return str(prefix + '_' + tstr + '_' + base.name)
                    #print(self.config['model_temp_filename'])
                    self.config['model_filename_redd'] = fpath
                    #self.config['model_temp_filenn'] = fpath
                else:
                    self.config['model_filename_redd'] = fpath
                    #self.config['model_temp_filenn'] = fpath
                    try:
                        return (prefix + '_' + tstr + '_' + self.config['temporary__string'])
                    except:
                        error_print('@')
                    ok_print('Wrote {} to path: {}'.format(base.name, fpath))
