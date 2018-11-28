from __future__ import print_function
observation_counter = 0
import cmd
import shutil
import contextlib
import io
import glob
import math
import os, os.path
import re
import shlex
import sys
import time
import numpy
from StringIO import StringIO
from pprint import pprint
from colorama import Fore, Back, Style, init
init()

import pyasad
from pyasad import Base
import FileGenFunctions as fg
import plot
from config import GlobalConfig
from plotter import main_plotter
import warnings
from chi_square_minimization import chi_square_minimization
#===============================================================================
def pre_loading_bar(i):
    print("")
    ok_print(" Reading Models...")
    print("")
    print ("|" + (" " * (i)) + "|")
    print("")
    sys.stdout.write("|")
#____________________________________________
def folder_checker(path):
    try:
        os.makedirs(path)
    except:
        pass
#===============================================================================
#inputs value entered by user in cmd
def safe_input(s):
    return raw_input(s)
#prints out the message 's' with the default and returns the default if the value is empty, otherwise it returns the entered value 'arg'
def safe_default_input(s, default=None):
    out = s + (" [%s]: " % default)				#out will be a concatenation of s and a variety of default values followed by the ':'
    arg = safe_input(out)					#prints out the message 's' with the default and returns the default if the value is empty, otherwise it returns the entered value 'arg'	#prints out and stores the entered values that follow into arg
    return default if arg == '' else arg

#replaces the quotes with white-space
def remove_quotes(text):
    return re.sub(r'^["\']|["\']$', '', text)

#slpits the string args without regarding any found quotations
def split_args(arg):
    if os.name == 'nt':
        posix = False
    else:
        posix = True
    return shlex.split(arg, posix=posix)

#creates a variable 'args' that stores the value of the string (x)
def parse_args(arg, required=False, expected=0, type=unicode):
    args = [ type(remove_quotes(x)) for x in split_args(arg) ]
    if expected > len(args):
        raise ValueError("Expected {} args got {}".format(expected, len(args)))
    if required and expected != len(args):
        raise ValueError("Require {} args got {}".format(expected, len(args)))
    return args

#analyzes a tuple into its logical syntactical components (checks each value of a tuple list)
def parse_tuple(arg, required=False, type=unicode, expected=0):
    args = arg.strip('()').split(',')
    args = tuple(type(arg) for arg in args if arg)				#equates args to a tuple list containing arg(of the type defined by the programmer during implementation of the function)
    if expected > len(args):									#checking for any errors in length of args
        raise ValueError("Expected {} args got {}".format(expected, len(args)))
    if required and expected != len(args):
        raise ValueError("Require {} args got {}".format(expected, len(args)))
    return args

#same function as parse_tuple but returns an int value
def parse_tuple_int(arg, *args, **kwargs):				#*args: takes unlimited regular arguments, prevents crashing as well as **kwargs
    return parse_tuple(arg, type=int, *args, **kwargs)
#returns boolean value depending on value chosen (yes/no) and prints the choice (either YES or NO)

def parse_yn(arg, default=False):
    try:
        choice = parse_args(arg, required=True, expected=1)
        choice = choice[0].upper()[0]                    #converts the entered 'y' and 'n' to capital letters
        if choice == 'Y':
            return True
        elif choice == 'N':
            return False
        else:                                            #if neither was true the function assumes the default
            err_msg = 'Unknown choice: %s Assuming: %s' % (choice, default)
            error_print(err_msg)
            raise ValueError(err_msg)
    except Exception as err:
        if default:
            ok_print('YES')
        else:
            error_print('NO')
        return default
#prints out the question and the [y/n] choice in cmd

def parse_input_yn(question, default=False):
    yn = ['y', 'n']
    index = int(not default)
    yn[index] = yn[index].upper()                      #sets the default option to a capital value
    marker = '? [%s/%s]: ' % tuple(yn)
    choice = safe_input(question + marker)
    return parse_yn(choice, default)

#prints out text with color (used in the next 3 functions
def color_print(text, color):
    print(color + text)
    print(Fore.RESET + Back.RESET + Style.RESET_ALL)

#prints out the red colored texts
def error_print(text):
    color_print(text, Fore.RED)

#prints out the green colored texts
def ok_print(text):
    color_print(text, Fore.GREEN)

#prints out the blue colored texts
def info_print(text):
    color_print(text, Fore.BLUE)

#creates a list of input files
def list_files(directory, pattern=".*"):
    regex = re.compile(pattern)
    in_dir = os.path.abspath(directory)
    in_files = [
        os.path.join(in_dir, f)
        for f in os.listdir(in_dir)
        if re.match(regex, os.path.basename(f))
    ]
    return in_files

def base_command(type):
    def command(self, arg):
        try:
            args = parse_args(arg, expected=2)
            subcmd = args[0]
            args = args[1:]
            name = type.__name__
            name = name[len('do_'):] if name.startswith('do_') else name
            command = '_'.join([name, subcmd])
            cmd_arg = ' '.join(args)
            self.onecmd(command + ' ' + cmd_arg)
        except Exception as err:
            error_print(unicode(err))
    return command

#===============================================================================

class Shell(cmd.Cmd, object):

    def __init__(self, *args, **kwargs):
        self._values = list()
        cmd.Cmd.__init__(self, *args, **kwargs)

    def default(self, line):              #default print statement
        print("Unknown command " + line)

#changes the value of values depending on the size
    @contextlib.contextmanager
    def mutate_values(self, index):
        temp = self.values
        if len(index) == 1:
            self.values = [self.values[index[0]]]
        elif len(index) == 2:
            self.values = list(self.values[index[0]:index[1]])		#converts the values of index[0] and index[1] to a list and stores it in values

        yield   #yield must be present when using @contextlib.contextmanager even if it remained empty

        if len(index) == 1:
            temp[index[0]] = self.values[0]
        elif len(index) == 2:
            temp[index[0]:index[1]] = self.values
        self.values = temp

#sets the index to the return value of the parse_tuple function
    def do_index(self, arg):
        try:
            args = parse_args(arg, expected=2)
            index_arg = args[0]
            submcd = args[1:]
            index = parse_tuple(index_arg, type=int, expected=1)
            with self.mutate_values(index):
                self.onecmd(' '.join(subcmd))
        except Exception as err:
            error_print(unicode(err))

    @base_command
    def do_set(self, arg):
        pass

    @property
    def values(self):
        return self._values
    @values.setter
    def values(self, values):
        self._values = values

#===============================================================================

class Base_Shell(Shell):
    asad_type = pyasad.Base
    #from pyasad import Base
    #from Base import continuum2 , closest

    def do_help(self, arg):
        print('base [list | read | directory]')
    #Lists the current bases
    def do_list(self, arg):
        "List the current bases"
        if not self.values:            #escapes code if values is empty
            print('Empty')
            return

        len_cols = (10, 20, 10, 10)
        ncols = len(len_cols)
        (col_str, sep_str) = ("{:^%d}|", "{:-^%d}+")			#number formatting: makes sure numbers are printed in a specific format
        fmt_col = '|' + (col_str * ncols) % len_cols
        sep = '+' + ((sep_str * ncols) % len_cols).format(*['']*ncols)

        print (sep)
        print(fmt_col.format('Index', 'Name', 'Num', 'Num_WL'))
        print(sep)
        for (i,m) in enumerate(self.values):
            print(fmt_col.format(i, m.name[:15], m.num, m.num_wl))
        print(sep)

#reads from a file and checks for any exceptions
    def do_read(self, arg,choice=0):
        "Read from a file"
        try:    #71444
			if choice == 0:
				path = os.path.abspath(parse_args(arg, expected=1)[0])
				base = self.asad_type(path=path)
				self.values.append(base)
				ok_print("Read OK: {}".format(path))
				ok_print("Wavelength Step: {}".format(base.wavelength_step))
			elif choice == 1:
				path = os.path.abspath(parse_args(arg, expected=1)[0])
				base = self.asad_type(path=path)
				self.values.append(base)
				#ok_print("Read OK: {}".format(path))
				#ok_print("Wavelength Step: {}".format(base.wavelength_step))
        except Exception as err:
            error_print("Failed to read file")
            error_print(unicode(err))
            raise err

    #reads all the files in the specified directory and checks for any exceptions
    def do_directory(self, arg):
        "Read all the files in a directory"
        indexer = 0
        global observation_counter
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise(RuntimeError('Must be a directory'))
            for f in list_files(path):
                obj = self.asad_type(path=f)
                self.values.append(obj)
                ok_print("Read OK: {}".format(f))
                indexer += 1
            observation_counter = indexer
        except Exception as err:
            error_print('Directory read failed')
            error_print(unicode(err))
            raise err
  #reads a file depending on the path specified
    def do_read_file_directory(self, arg):
        global observation_counter
        "Read a file or a directory depending on the path"
        indexer = 0
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if os.path.isdir(path):
                self.do_directory(path)
            elif os.path.isfile(path):
                self.do_read(path)
            else:
                files = glob.glob(path)
                if not files:
                    raise ValueError('Invalid Path')
                for f in files:
                    obj = self.asad_type(path = f)
                    self.values.append(obj)
                    ok_print("Read OK: {}".format(f))
                    indexer += 1
                observation_counter = indexer
        except Exception as err:
            error_print('File or Directory Read Error')
            error_print(unicode(err))
            raise err

#writes output to the specified output directory
    def do_write(self, arg, prefix='',choice=0):
        "Write current bases to a directory"
        path = parse_args(arg, expected=1)[0]
        if not os.path.isdir(path):
            error_print('Must be a directory not a path: {}'.format(path))
            return
        if choice == 0:
            for base in self.values:
                tstr = time.strftime('%H_%M_%S+%d-%m-%y', time.localtime())
                fpath = os.path.join(path, prefix + '_' + tstr + '_' + base.name)
                if os.path.exists(fpath):
                    error_print('{} already exists, Skipping'.format(fpath))
                    raise Exception('file already exists')
                else:
                    print(base.format(), file=io.open(fpath, 'w'))
                    ok_print('Wrote {} to path: {}'.format(base.name, fpath))
        elif choice == 1:
            for base in self.values:
                tstr = time.strftime('%H_%M_%S+%d-%m-%y', time.localtime())
                fpath = os.path.join(path, prefix + '_' + tstr + '_' + base.name)
                if os.path.exists(fpath):
                    error_print('{} already exists, Skipping'.format(fpath))
                    raise Exception('file already exists')
                else:
                    print(base.format(), file=io.open(fpath, 'w'))
                    #ok_print('Wrote {} to path: {}'.format(base.name, fpath))
 #normalization of the base shell
    def do_normalize(self, arg , filename , choice):
        "Normalize a base"
        if choice == 1:
            wavelength = parse_args(arg, expected=1, type=float)[0]
            for (i, base) in enumerate(self.values):
                #print(i)
                self.values[i] = base.normalize(wavelength)     	#calls normalize calculation from base class in pyasad.py
                ok_print('Normalized: {}'.format(base.name))
                #print(self.values)
        elif choice == 2:
            for (i,base) in enumerate(self.values):
                #print(i)
                self.values[i] = base.normalize_all(filename)
                #print("\nOK\n")
            ok_print('Normalized the entire range')

        else:
            return False

   #prints out the name matrix in an organized list
    def do_name(self, arg):
        for base in self.values:
            pprint(base.name)

#sets the name of the output files generated
    def do_set_name(self, arg):
        name = parse_args(arg, expected=1)[0]
        for base in self.values:
            base.name = name
        ok_print('Name set to: {}'.format(name))

    #outputs the name of the base and the matrix of wavlengths from the range specified (start-end)/integer tuple
    def do_wavelength_index(self, arg,choice=0):
        if choice == 0:
            try:
                (start, end) = parse_tuple_int(arg, expected=2)
                if end == -1:
                    end = None
                for base in self.values:
                    print('{}: {}'.format(base.name, base.wavelength_str(start, end)))
                print('\n')
            except ValueError as value_error:
                error_print('wavelength index needs 2 args: (start, end)')
                raise value_error
            except IndexError as index_error:
                error_print('wavelength index error')
                error_print(str(index_error))
                raise index_error
            except TypeError as type_err:
                error_print('wavelength index must be an integer')
                raise type_error
        else:
            try:
                (start, end) = parse_tuple_int(arg, expected=2)
                if end == -1:
                    end = None
                for base in self.values:
                    pass
                    #print('{}: {}'.format(base.name, base.wavelength_str(start, end)))
                #print('\n')
            except ValueError as value_error:
                #error_print('wavelength index needs 2 args: (start, end)')
                raise value_error
            except IndexError as index_error:
                #error_print('wavelength index error')
                #error_print(str(index_error))
                raise index_error
            except TypeError as type_err:
                #error_print('wavelength index must be an integer')
                raise type_error

    #prints the wavelength matrix from the set range (start-end)/non-integer tuple
    def do_wavelength_range(self, arg):
        try:
            (start, end) = parse_tuple(arg, expected=2, type=float)
            for base in self.values:
                pprint(base.wavelength_range(start, end))
        except ValueError as value_error:
            error_print('wavelength range (wl_start, wl_end)')
            raise value_error
        except IndexError as index_error:
            error_print('invalid wavelength range, choosing entire range')
            error_print(str(index_error))
            raise index_error
        except TypeError as type_error:
            error_print('wavelength range must be an integer')
            raise type_error

    #prints out wavelength matrix in a different format
    def do_set_wavelength_index(self, arg):
        try:
            (start, end) = parse_tuple(arg, expected=2, type=int)
            for (i, base) in enumerate(self.values):
                self.values[i] = base.wavelength_set_index(start, end)
                ok_print('Wavelength index set: ({}, {})'.format(start, end))
        except ValueError as value_error:
            error_print('set_wavelength_index (start, end)')
            raise value_error

    #sets the start value of the wavelengths
    def do_set_wavelength_start(self, arg):
        try:
            start = parse_tuple(arg, expected=1, type=float)[0]
            for (i, base) in enumerate(self.values):
                self.values[i] = base.wavelength_set_start(start)
                ok_print('Wavelength start set to: {}'.format(start))
        except ValueError as value_error:
            error_print('set_wavelength_start wl_start')
            raise value_error
        except IndexError as index_error:
            error_print('invalid wavelength start, wavelength start not set')
            error_print(str(index_error))
            pass
        except TypeError as type_error:
            error_print('wavelength start must be a float')
            raise type_error

    #sets the end value of the wavelengths
    def do_set_wavelength_end(self, arg):
        try:
            end = parse_tuple(arg, expected=1, type=float)[0]
            for (i, base) in enumerate(self.values):
                self.values[i] = base.wavelength_set_end(end)
                ok_print('Wavelength end set to: {}'.format(end))
        except ValueError as value_error:
            error_print('set_wavelength_end wl_end')
            raise value_error
        except IndexError as index_error:
            error_print('invalid wavelength end, wavelength end not set')
            error_print(str(index_error))
            pass
        except TypeError as type_error:
            error_print('wavelength end must be a float')
            raise type_error

    #sets both the start and end values
    def do_set_wavelength_range(self, arg, choice=0):
        if choice == 0:
            try:
                (start, end) = parse_tuple(arg, expected=2, type=float)
                for (i, base) in enumerate(self.values):
                    self.values[i] = base.wavelength_set_range(start, end)
                    ok_print('Wavelength range set: ({}, {})'.format(start, end))
            except ValueError as value_error:
                error_print('set_wavelength_range (wl_start, wl_end)')
                raise value_error
            except IndexError as index_error:
                error_print('invalid wavelength range, choosing entire range')
                error_print(str(index_error))
                pass
            except TypeError as type_error:
                error_print('wavelength range must be floats')
                raise type_error
        else:
            try:
                (start, end) = parse_tuple(arg, expected=2, type=float)
                for (i, base) in enumerate(self.values):
                    self.values[i] = base.wavelength_set_range(start, end)
                    #ok_print('Wavelength range set: ({}, {})'.format(start, end))
            except ValueError as value_error:
                #error_print('set_wavelength_range (wl_start, wl_end)')
                raise value_error
            except IndexError as index_error:
                #error_print('invalid wavelength range, choosing entire range')
                #error_print(str(index_error))
                pass
            except TypeError as type_error:
                #error_print('wavelength range must be floats')
                raise type_error

    #prints out the fluxes in rows s1-e1 and columns s2-e2
    def do_flux(self, arg):
        try:
            args = parse_args(arg, expected=2)
            (s1, e1) = parse_tuple_int(args[0], expected=2)
            (s2, e2) = parse_tuple_int(args[1], expected=2)
            for base in self.values:
                pprint(base.flux[s1:e1, s2:e2])
        except ValueError as value_error:
            error_print('flux needs 5 args: index (start, end) (wl_start, wl_end)')
            raise value_error
        except IndexError as index_error:
            error_print('flux index error')
            raise index_error
        except TypeError as type_error:
            error_print('flux index and range must be integers')
            raise type_error

    #sets a wavelength matrix that starts at the entered number and stores the interpolated wavelengths
    def do_interpolation_wavelength_start(self, arg):
        args = parse_args(arg, expected=2, type=float)
        interp = args[0]
        wavelength = args[1]
        for base in self.values:
            wl_start = base.restrict_wavelength_start_by_interpolation_step(interp, wavelength)
            ok_print('{}: set starting wavelength to: {} using interpolation step: {}'.format(
                 base.name, wl_start, interp))

	#smooths the data (observation and model) and outputs a file with the new data
    def do_smoothen(self, arg):
        try:
            args = parse_args(arg, expected=1)
            interp = float(args[0])
            for (i, base) in enumerate(self.values):
                self.values[i] = base.smoothen(
                    interp,
                    name="smoothed_" + base.name,
                    step=base.wavelength_step)
                ok_print('Smoothed: {}'.format(base.name))
        except ValueError as value_error:
            error_print('Interpolation step needed')
            raise value_error
        except TypeError as type_error:
            error_print('Interpolation step must be a float')
            raise type_error

#===============================================================================

class Model_Shell(Base_Shell):
    asad_type = pyasad.Model
    def __init__(self):
        self._values = list()
        self.config = GlobalConfig()


    #closest is a function that works with the normalize_all function from pyasad , normalize_all handles entire range normalization.
    def closest(self, input,val):
        """Return the closest value in input to val"""
        array = np.array(input)
        try:
                values = np.array(val)
                len(values)
        except TypeError:
                values = np.array([val])
        out = np.zeros(len(values),dtype=int)
        for i in xrange(len(values)):
                out[i] = np.argmin(abs(array-values[i]))        #In the event of more than one value return just
                                                                #the first one
        return np.squeeze(out)
    #continuum2 is a function that works with the normalize_all function from pyasad , normalize_all handles entire range normalization.
    def continuum2(self, wl,fobs,vel_mask=2000.,width=100.):
        """Computes the continuum of a spectrum by means of a median filter on the
           red part of the obtical spectrum and a cubic spline for the blue end.
                wl: Wavelenght vector

                fobs: Flux vector

                width: Width of the median filter in Angstroms

                vel_mask: Velocity dispersion for the Balemer lines mask in Km/s"""
        width=width/2.
        wl_balmer = np.loadtxt('balmer_air.txt',unpack=True,usecols=[0])
        cont_b, cont_r =np.loadtxt('blue_balmer_air_cont.txt',unpack=True)
        wl_balmer_b = []
        wl_balmer_r = []

        mask = np.array([True]*wl.size,dtype=bool)

        for i in xrange(len(wl_balmer)):
                wl_balmer_b.append(self.closest(wl,wl_balmer[i]*(1-vel_mask/3e5)))
                wl_balmer_r.append(self.closest(wl,wl_balmer[i]*(1+vel_mask/3e5)))
                mask[wl_balmer_b[i] : wl_balmer_r[i]] = False   #Creates the mask for each line

        wlm = wl[mask]
        fobsm = fobs[mask]

        cont = []

        for i in xrange(len(wlm)):
                cont.append(np.median(fobsm[self.closest(wlm,wlm[i]-width):self.closest(wlm,wlm[i]+width)]))

        cont_balmer_index = np.array([self.closest(wl,x) for x in cont_b + (cont_r-cont_b)/2.])

        #Create a new mask from the bluest end of the Balmer mask to the second to last
        #pixel where the spline and the median continuum match (spline wl range)
        mask = np.array([True]*wlm.size,dtype=bool)
        mask[self.closest(wlm,cont_b[0]):self.closest(wlm,wl[cont_balmer_index[-1]])] = False

        #Remove pixels from masked wavelength and flux within spline wavelength range
        wlm = wlm[mask]
        cont = np.array(cont)
        cont = cont[mask]

        ##Spline wavelength range in original wl array
        mask = np.array([False]*wl.size,dtype=bool)
        mask[self.closest(wl,cont_b[0]):cont_balmer_index[-1]] = True

        CSpline = spint.UnivariateSpline(wl[cont_balmer_index],fobs[cont_balmer_index],k=3,s=0)

        cont2 = CSpline(wl[mask])

        #Merge spline cont and wl with median cont and wl
        wlm = np.append(wlm,wl[mask])
        cont = np.append(cont,cont2)
        srt = wlm.argsort()
        wlm = wlm[srt]
        cont = cont[srt]

        IntLineal = spint.interp1d(wlm,cont,kind='linear')
        #return IntLineal(wl)
        try:
                return IntLineal(wl)
        except:
                #this corrects the ValueError in case the wl array starts bellow the interpolation range (wlm)
                #print "The blue end of the spectrum has been extrapolated from the last non-masked value"
                return np.pad(IntLineal(wl[self.closest(wl,wlm[0]):]), (wl.size-wl[self.closest(wl,wlm[0]):].size,0), 'edge')

    #reads files and prints out if they were read without errors
    def do_read(self, arg, format='DELGADO',choice=0,typee=None):
        global observation_counter
        try:
            if choice == 0:
				path = os.path.abspath(parse_args(arg, expected=1)[0])
				base = self.asad_type(path=path, format=format)
				self.values.append(base)
				ok_print("Read OK: {}".format(path))
				ok_print("Wavelength Step: {}".format(base.wavelength_step))

            elif choice == 1:
				path = os.path.abspath(parse_args(arg, expected=1)[0])
				base = self.asad_type(path=path, format=format)
				self.values.append(base)
        except Exception as err:
            error_print("Failed to read file")
            error_print(unicode(err))
            raise err
        if observation_counter == 0:
            observation_counter == 1
    #sets the starting ae for the model
    def do_set_age_start(self, arg):
        age_start = parse_args(arg, expected=1, type=float)[0]
        for model in self.values:
            model.age_start = age_start
            model.age = None

    #sets the age step for the model
    def do_set_age_step(self, arg):
        age_step = parse_args(arg, expected=1, type=float)[0]
        for model in self.values:
            model.age_step = age_step
            model.age = None
            print(model.age)

#===============================================================================

class Observation_Shell(Base_Shell):
    asad_type = pyasad.Observation
    def __init__(self):
        self._base = Base_Shell()
        #self._model = Model_Shell()
        self._values = list()
        #self._observation = Observation_Shell()
        self.config = GlobalConfig()
        #super(Object_Shell, self).__init__(*args, **kwargs)


    def do_normalize(self, arg , filename, choice):
        "Normalize a base"
        if choice == 1:
            wavelength = parse_args(arg, expected=1, type=float)[0]
            for (i, base) in enumerate(self.values):
                #print(i)
                self.values[i] = base.normalize(wavelength)     	#calls normalize calculation from base class in pyasad.py
                ok_print('Normalized: {}'.format(base.name))
                #print(self.values)
        elif choice == 2:
            for (i,base) in enumerate(self.values):
                #print(i)
                self.values[i] = base.normalize_all(filename)
                #print("\nOK\n")
            ok_print('Normalized the entire range')

        else:
            return False
    #sets the reddening step for the observation files
    def do_set_reddening_step(self, arg):
        reddening_step = parse_args(arg, expected=1, type=float)[0]
        for obsv in self.values:
            obsv.reddening_step = reddening_step

    #sets reddening start value
    def do_set_reddening_start(self, arg):
        reddening_start = parse_args(arg, expected=1, type=float)[0]
        for obsv in self.values:
            obsv.reddening_start = reddening_start

    #corrects to the reddening values in observation files
    def do_redshift(self, arg):
        try:
            [start, end, step] = parse_args(arg, expected=3, type=float)
            for (i, observation) in enumerate(self.values):
                self.values[i] = observation.reddening_shift(start, end, step)
                ok_print('Reddening Corrected: {}'.format(observation.name))
        except ValueError as value_error:
            error_print('Redshift: start end step needed')
            raise value_error
        except TypeError as type_error:
            error_print('Redshift: start, end and step must be floats')
            raise type_error

#===============================================================================

class Plot_Shell(Shell):
    pass

#===============================================================================

class Object_Shell(Base_Shell):
    asad_type = pyasad.Asad
    #self.config['plot_surface_dir'] = ""

    def __init__(self, *args, **kwargs):
        self._base = Base_Shell()
        self._model = Model_Shell()
        self._observation = Observation_Shell()
        self.config = GlobalConfig()
        super(Object_Shell, self).__init__(*args, **kwargs)

	#appends value of object to the values 2D-matrix from [me:ms , oe:os]
    def do_new(self, arg):
        args = parse_args(arg, expected=2)
        index = [parse_tuple(x, expected=2, type=int) for x in args]
        (ms, me) = index[0]
        (os, oe) = index[1]
        me = None if me == (-1) else me
        oe = None if oe == (-1) else oe
        for model in self.model.values[ms:me]:
            for obsv in self.observation.values[os:oe]:
                obj = pyasad.Asad.from_observation_model(obsv, model)
                self.values.append(obj)

    #prints the observation/model matrix names
    def do_list(self, arg):
        for obj in self.values:
            pprint(obj.name)

    #calculates the statistics of the data
    def do_calculate_chosen_model(self, arg,choice=0,stat_testt=""):
        try:
            if choice == 0:
                stat_test = pyasad.Statistics.ks_2_sample_freq_test if arg == 'KS' else pyasad.Statistics.chi_squared_freq_test
                for obj in self.values:
                    if len(obj.model.wavelength) != len(obj.model.wavelength):
                        raise Exception(
                            ('Number of rows in observation: {} and model: {} not equal' +
                             'Observation : {} Model : {}').format(
                                 obj.observation.name, obj.model.name,
                                 obj.num_observation, obj.num_model
                             ))
                    obj.stat_test = stat_test
                    obj.calculate_chosen_model()

                    if self.config['temporary_choice'] == 0:
                        ok_print('Calculated Min Age and Reddening: %s' % obj.name)
            else:
                stat_test = pyasad.Statistics.ks_2_sample_freq_test if arg == 'KS' else pyasad.Statistics.chi_squared_freq_test
                for obj in self.values:
                    if len(obj.model.wavelength) != len(obj.model.wavelength):
                        raise Exception(
                            ('Number of rows in observation: {} and model: {} not equal' +
                             'Observation : {} Model : {}').format(
                                 obj.observation.name, obj.model.name,
                                 obj.num_observation, obj.num_model
                             ))
                    obj.stat_test = stat_test
                    obj.calculate_chosen_model()

                    #if self.config['temporary_choice'] == 0:
                    #    ok_print('Calculated Min Age and Reddening: %s' % obj.name)
        except Exception as err:
            error_print('Error calculating best Reddening/Age match')
            error_print(unicode(err))
            raise err

    #prints formatted file names
    def do_chosen(self, arg):
        if not self.values:
            print('Empty')
            return

        len_cols = (5, 15, 10, 10)
        ncols = len(len_cols)
        (col_str, sep_str) = ("{:^%d}|", "{:-^%d}+")
        fmt_col = '|' + (col_str * ncols) % len_cols
        sep = '+' + ((sep_str * ncols) % len_cols).format(*['']*ncols)

        print (sep)
        print(fmt_col.format('Index', 'Name', 'Min_Age', 'Min_Reddening'))
        print(sep)
        for (i, obj) in enumerate(self.values):
            print(fmt_col.format(
                i, obj.name[:15], obj.min_age, obj.min_reddening))
        print(sep)

    def do_write_chosen(self, arg, config=None):

        def write_chosen(path, values):
            with io.open(path, 'w') as f:
                for obj in values:
                    f.write(obj.format_chosen())
                    ok_print('Wrote %s to %s' % (obj.name, path))
                if config:
                    buff = StringIO()
                    buff.write(unicode('\n'))
                    config.write(buff)
                    f.write(unicode(buff.getvalue()))

        path = os.path.abspath(parse_args(arg, expected=1)[0])
        if os.path.isdir(path):
            for obj in self.values:
                fname = config['object_test_statistic'] + '_' + 'result_of_%s' % obj.name
                fpath = str(os.path.join(path, fname))
                #print(fpath)
                write_chosen(fpath, [obj])
            #print(fpath)
            return fpath
        else:
            write_chosen(path, self.values)
            #print(path)
            return path

    @base_command
    def do_plot(self, arg):
        pass

    #plots the surface graph and prints out directory name it got saved in
    def do_plot_surface(self, arg, format='', title=None):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise RuntimeError('Must be a directory')
            for obj in self.values:
                plot.surface(obj, outdir=path, save=True, format=format, title=title)
                ok_print('Plotted surface %s to %s' % (obj.name, path))
        except Exception as err:
            error_print(unicode(err))
            raise err

    #plots the scatter graph and prints out directory name it got saved in
    def do_plot_scatter(self, arg, ages=[], reddenings=[], format='', title=None):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise RuntimeError('Must be a directory')
            for obj in self.values:
                plot.scatter(obj, ages=ages, reddenings=reddenings,
                             outdir=path, save=True, format=format, title=title)
                ok_print('Plotted scatter %s to %s' % (obj.name, path))
        except Exception as err:
            error_print(unicode(err))
            raise err
#////////////////////////////////////////////////////////////////////////////////
    #plots the residual from the chi-squared best match
    def do_plot_residual_match(self,twoModels, arg, format='', title=None,chi_result=[] ,choice=0,key=False):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise RuntimeError('Must be a directory')

            if twoModels:   #If two models are passed into the program
                if chi_result == []:
                    limit = len(self.values)/2
                    for i in range(0, limit):
                        if key == True:
                            ok_print('Please specify the legend parameters for plot with observation -> '+self.values[i].observation.original_name)
                            observationKey = safe_default_input('Observation Key', 'Default')
                            modelKey1 = safe_default_input('Model 1 Key', 'Default')
                            modelKey2 = safe_default_input('Model 2 Key','Default')
                        else:
                            observationKey = 'Default'
                            modelKey1 = 'Default'
                            modelKey2 = 'Default'
                        plot.residual_match(self.values[i],self.values[i+limit], outdir=path, observationKey=observationKey, modelKey1=modelKey1, modelKey2=modelKey2, save=True, format=format, title=title)
                        ok_print('Plotted residual match %s & %s to %s' % (self.values[i].name,self.values[i+limit].name, path))
                else:
                    i = -1
                    #limit = len(self.values)/2
                    ndxxx = 0
                    for j in chi_result:
                        i += 1
                        for k in j:
                            if os.name == 'nt':
                                filename = k[k.rfind("\\") + 1:]
                                #print("filename:  " + filename)
                                ndx1 = filename[filename.rfind("-") + 1:]
                                #print("ndx1:      " + ndx1)
                                ndx2 = ndx1[ndx1.find("_")+1:]
                                #print("ndx2:      " + ndx2)
                                ndx3 = ndx2[ndx2.find("_")+1:]
                            else:
                                filename = k[k.rfind("/") + 1:]
                                ndx1 = filename[filename.rfind("-") + 1:]
                                ndx2 = ndx1[ndx1.find("_")+1:]
                                ndx3 = ndx2[ndx2.find("_")+1:]
                            try:
                                for value_index in xrange(0,len(self.values)):
                                    if self.values[value_index].name == ndx2:
                                        ndxxx = value_index
                                        break
                            except Exception as e:
                                print("@Error : " + str(e))
                            try:
                                if key == True:
                                    ok_print('Please specify the legend parameters for plot with observation -> '+self.values[i].observation.original_name)
                                    observationKey = safe_default_input('Observation Key', 'Default')
                                    modelKey1 = safe_default_input('Model 1 Key', 'Default')
                                    modelKey2 = safe_default_input('Model 2 Key','Default')
                                else:
                                    observationKey = 'Default'
                                    modelKey1 = 'Default'
                                    modelKey2 = 'Default'
                                plot.residual_match(self.values[i],self.values[ndxxx], outdir=path, observationKey=observationKey, modelKey1=modelKey1, modelKey2=modelKey2, save=True, format=format, title=title)
                                ok_print('Plotted residual match %s & %s to %s' % (self.values[i].name,self.values[ndxxx].name, path))
                            except Exception as e:
                                print("@Error : " + str(e))

            else:
                for obj in self.values:
                    if key == True:
                        ok_print('Please specify the legend parameters for plot with observation -> '+obj.observation.original_name)
                        observationKey = safe_default_input('Observation Key', 'Default')
                        modelKey = safe_default_input('Model Key', 'Default')
                    else:
                        observationKey = 'Default'
                        modelKey = 'Default'
                    plot.residual_match_one_model(obj, outdir=path, observationKey=observationKey, modelKey=modelKey, save=True, format=format, title=title)
                    ok_print('Plotted residual match %s to %s' % (obj.name, path))

        except Exception as err:
            error_print(unicode(err))
            raise err
#/////////////////////////////////////////////////////////
    def do_plot_residual(self, arg, format='', title=None):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])
            if not os.path.isdir(path):
                raise RuntimeError('Must be a directory')
            for obj in self.values:
                plot.residual(obj, outdir=path, save=True, format=format, title=title)
                ok_print('Plotted residual %s to %s' % (obj.name, path))
        except Exception as err:
            error_print(unicode(err))
            raise err
    #test
    def do_plot_surface_error(self, arg, format=''):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])    #abspath returns the normalized absolutized version of parse_args(...)[0]
            if not os.path.isdir(path):
                raise RuntimeError('Must be a directory')
            for obj in self.values:
                obj.calculate_stat_delta_level()
                plot.surface_error(obj, outdir=path, save=True, format=format)
                ok_print('Plotted surface error %s to %s' % (obj.name, path))
        except Exception as err:
            error_print(unicode(err))
            raise err

    #plots the scatter tiles and stores them in a defined path
    def do_plot_scatter_tile(self, arg, format=''):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])#abspath returns the normalized absolutized version of parse_args(...)[0]
            if not os.path.isdir(path):   #checks if the directory in the declared path exists
                raise RuntimeError('Must be a directory')
            obj_len = len(self.values)
            ncols = 3
            nrows = obj_len / ncols
			#matrix of the model ages
            original_ages = {
                'Ya'  : 6.48,
                'Yb1' : 6.88,
                'Yb2' : 6.88,
                'Yb3' : 6.88,
                'Yc'  : 7.30,
                'Yd'  : 7.60,
                'Ye'  : 7.78,
                'Yf'  : 8.10,
                'Yg'  : 8.44,
                'Yh'  : 8.70,
                'Ia'  : 9.00,
                'Ib'  : 9.54,
            }
            for x in self.values:
                title = os.path.splitext(x.observation.original_name)[0]#splits the pathname of (x.observation.original_name)[0] to (root,ext)
                x.observation.original_name = title   #changes the name to the defined 'title'

            observations = ['Ya', 'Yb1', 'Yb2', 'Yb3', 'Yc', 'Yd', 'Ye', 'Yf', 'Yg', 'Yh', 'Ia', 'Ib']
            #creates matrix of known observations
            self.values.sort(key=lambda x: observations.index(x.observation.original_name))

            plot.scatter_tile(self.values, nrows, ncols, outdir=path,
                              original_ages=original_ages,
                              save=True, format=format)            #plots the scatter tiles in the values matrix
            ok_print('Plotted scatter tile %s' % path)
        except Exception as err:
            error_print(unicode(err))
            raise err

    #plots the surface tiles and stores them in a defined path
    def do_plot_surface_tile(self, arg, format=''):
        try:
            path = os.path.abspath(parse_args(arg, expected=1)[0])     #abspath returns the normalized absolutized version of parse_args(...)[0]
            if not os.path.isdir(path):         #checks if the directory in the declared path exists
                raise RuntimeError('Must be a directory')
            obj_len = len(self.values)
            ncols = 3
            nrows = int(math.ceil(float(obj_len) / ncols))
            plot.surface_tile(self.values, nrows, ncols, outdir=path,
                              save=True, format=format)
            ok_print('Plotted surface tile %s' % path)
        except Exception as err:
            error_print(unicode(err))
            raise err

    #getters for class Object_Shell
    @property
    def base(self):
        return self._base

    @property
    def model(self):
        return self._model

    @property
    def observation(self):
        return self._observation

#===============================================================================

def prompt_command_2(func):
    def prompt_function(self):
        while True:
            try:
                func(self)
            except Exception as err:
                error_print(unicode(err))
                continue
            break
    return prompt_function

def prompt_command(func):
    def prompt_function(self):
        try:
            func(self)
        except Exception as err:
            error_print(unicode(err))
            raise err
    return prompt_function


#-------------------------------------------------------------------------------
#Object_Shell is a base class
#class where we run all the pre functions
class Run_Shell(Object_Shell):

    def __init__(self, *args, **kwargs):
        self.object = Object_Shell()                             #calling Object_Shell class
        self.config = GlobalConfig()                             #calling config file-GlobalConfig class
        self.fpath = ""
        #self = ''
        super(Run_Shell, self).__init__(*args, **kwargs)         #gain access to inherited methods

    def update_config(self):
        self.config.write_config_file()

    @prompt_command
    def previousAnalysisObservation(self):
        print("Current Wavelength Range: ")
        		#calling (do_wavelength_index)function in (Base_Shell)class
        self.observation.do_wavelength_index('(0, -1)')
        		#call (do_set_wavelength_start) and call default start 3800 from default.conf
        self.observation.do_set_wavelength_start(self.config['observation_wavelength_start'])
        		#if the choice is Y for smooth: call (do_smoothen) and call the default interpolation_step = 3
        """if parse_yn(self.config['choices_smooth_observation']):
            self.observation.do_smoothen(self.config['observation_interpolation_step'])"""
                #call (do_set_wavelength_end) and call the default end 6230
        self.observation.do_set_wavelength_end(self.config['observation_wavelength_end'])
        		#if the choice is Y:call (do_write) and (smoothen_output_directory = data/observations) and prefix = 'smoothed_'
        if parse_yn(self.config['choices_output_smoothed_observation']):
            self.observation.do_write(self.config['observation_smoothen_output_directory'], prefix = 'smoothed_')
        #if Y: call(do_redshift) and (reddening_start and reddening and reddening_step) [0,0.5,0.01]
        if parse_yn(self.config['choices_reddening_correction']):
            self.observation.do_redshift(' '.join([self.config['observation_reddening_start'],
                                                   self.config['observation_reddening'],
                                                   self.config['observation_reddening_step']]))
		#if Y: call (do_normalize) and ormalize_wavelength = 5870
        if parse_yn(self.config['choices_normalize_wavelength']):
            self.observation.do_normalize(self.config['observation_normalize_wavelength'], self.config['observation_filename'] , self.config['normalization_norm_choice_number'])

        #if Y: call (do_write) and (output_directory = data/observations) and prefix = 'normalized_'
        if parse_yn(self.config['choices_output_observation']):
            temp__ = 0
            temp__ = self.config['object_temp_path_ndx']
            self.config['object_temp_path_ndx'] == -1
            if self.config['normalization_norm_choice_number'] == 2:
                pass
            else:
                self.observation.do_write(self.config['observation_output_directory'],prefix = 'normalized_')
            self.config['object_temp_path_ndx'] == temp__

    @prompt_command
    def previousAnalysisModel(self):
        if parse_yn(self.config['choices_set_age_start_and_step']):
            self.model.do_set_age_start(self.config['model_age_start'])
            self.model.do_set_age_step(self.config['model_age_step'])
			#if set_age_start_and_step is Y: call (do_set_age_start) and age_start = 0.0
			#call (do_set_age_step) and age_step = 0.2
        if parse_yn(self.config['choices_smooth_observation']):
            self.model_interpolation_wavelength_start_2()
            self.model_smoothen()	#if choices_smooth_observation is Y : call (model_interpolation_wavelength_start_2) and (model_smoothen) no class
        else:
            if parse_yn(self.config['choices_smooth_model']):
                self.model_interpolation_wavelength_start_no_obsv_smoothed()
                self.model_smoothen_no_obsv_smoothed()
        self.object.do_calculate_chosen_model(self.config['object_test_statistic'])

		#if choices_smooth_model is Y: call (model_interpolation_wavelength_start_no_obsv_smoothed)
		#call (model_smoothen_no_obsv_smoothed)
		#call (do_calculate_chosen_model) and (test_statistic = chi-squared)

    @prompt_command
    def previousOutputs(self):
		#if choices_output_models is Y: call (model_output): it'll call output_directory = data/models and (do_write)
        if parse_yn(self.config['choices_output_models']):
            self.model_output()
		#if choices_output_reddening_age_files is Y:call (object_output): it'll call output_directory = data/objects and (do_write)

        if parse_yn(self.config['choices_output_reddening_age_files']):
            self.object_output(self.config['choices_object_output'])
		#if choices_output_best_reddening_age_match is Y:call (object_output_chosen): it'll call chosen_directory = data\results and (do_write_chosen)
        if parse_yn(self.config['choices_output_best_reddening_age_match']):
            self.object_output_chosen()
		#if choices_output_surface_plots is Y: call (plot_surface_output):it'll call surface_directory = data/plots and output_format = eps
        if parse_yn(self.config['choices_output_surface_plots']):
            self.plot_surface_output()
		#if choices_output_best_spectra_match_plots is Y:call (plot_scatter_output):it'll call scatter_directory = data\Results
        if parse_yn(self.config['choices_output_best_spectra_match_plots']):
            self.plot_scatter_output()
		#if choices_output_residual_plots is Y:call (plot_residual_match_output):it'll call residual_match_directory = data\results and output_format = eps
        if parse_yn(self.config['choices_output_residual_plots']):
            self.plot_residual_match_output()
		#if choices_output_detailed_residual_plots is Y:call (plot_residual_output)
        if parse_yn(self.config['choices_output_detailed_residual_plots']):
            self.plot_residual_output()
		#if Y: call (plot_surface_title_output)
        if parse_yn(self.config['choices_output_surface_title_plot']):
            self.plot_surface_title_output()


    def model_read(self, fileName=None,choice=0):
        if choice != 1:
            #call MODEL_FORMATS from pyasad file/set the model default format as INTERMEDIATE
            model_format = safe_default_input(
                'What is the format of your model (' + ', '.join(pyasad.Model.MODEL_FORMATS) + ')',
                self.config['model_format']
            )
            #print error if input not from ['DELGADO', 'GALAXEV', 'MILES', 'INTERMEDIATE']
            while model_format not in pyasad.Model.MODEL_FORMATS:
                error_print('Please enter a valid model format')
                model_format = safe_default_input(
                    'What is the format of your model (' + ', '.join(pyasad.Model.MODEL_FORMATS) + ')',
                    self.config['model_format']
                )

    		#rewrite the model_format to the model we choose
            self.config['model_format'] = model_format
            ok_print("Model format set to {}".format(self.config['model_format']))
            		#if file name is empty: call input_directory = data\models\MILESres3.6.txt
            if fileName is None:
                self.config['model_input_directory'] = safe_default_input(
                    'Enter the model file (including the path) ',
                    self.config['model_input_directory']
                )
    		#if not: call the file name (suppose all pre data is saved )
            else:
                self.config['model_input_directory'] = safe_default_input(
                    'Enter Model File (including the path) ',
                     fileName
                )
            #call (do_read)for reading from a file: call input_directory = data\models\MILESres3.6.txt and format = INTERMEDIATE
            self.model.do_read(
                self.config['model_input_directory'],
                format=self.config['model_format']
            )
        else:
            #call MODEL_FORMATS from pyasad file/set the model default format as INTERMEDIATE
            model_format = self.config['model_format']
            #print error if input not from ['DELGADO', 'GALAXEV', 'MILES', 'INTERMEDIATE']
            while model_format not in pyasad.Model.MODEL_FORMATS:
                error_print('Please enter a valid model format')
                model_format = safe_default_input(
                    'What is the format of your model' + ', '.join(pyasad.Model.MODEL_FORMATS) + ')',
                    self.config['model_format']
                )

    		#rewrite the model_format to the model we choose
            #self.config['model_format'] = model_format
            #ok_print("Model format set to {}".format(self.config['model_format']))
            		#if file name is empty: call input_directory = data\models\MILESres3.6.txt
            #full_path = ''
            #fformat = '.' + format
            fileofwork = str(self.config['model_msp_output'])
            """if os.name == 'nt':
                full_path = fileofwork + '\\' + fileName
                #full_path = output + '\\' + da_file
            elif os.name == 'mac' or os.name == 'posix':
                full_path = fileofwork + '/' + fileName"""
            if fileName is None:
                    self.config['model_input_directory'] = fileName
    		#if not: call the file name (suppose all pre data is saved )
            else:
                self.config['model_input_directory'] = fileName
            #call (do_read)for reading from a file: call input_directory = data\models\MILESres3.6.txt and format = INTERMEDIATE
			#lowlowlow
            self.model.do_read(self.config['model_input_directory'],format=self.config['model_format'] , choice=1)


    def model_read_folder(self):
        #call MODEL_FORMATS from pyasad file/set the model default format as INTERMEDIATE
        model_format = safe_default_input(
            'What is the format of your model (' + ', '.join(pyasad.Model.MODEL_FORMATS) + ')',
            self.config['model_format']
        )
        #print error if input not from ['DELGADO', 'GALAXEV', 'MILES', 'INTERMEDIATE']
        while model_format not in pyasad.Model.MODEL_FORMATS:
            error_print('Please enter a valid model format')
            model_format = safe_default_input(
                'What is the format of your model (' + ', '.join(pyasad.Model.MODEL_FORMATS) + ')',
                self.config['model_format']
            )

        #rewrite the model_format to the model we choose
        self.config['model_format'] = model_format
        ok_print("Model format set to {}".format(self.config['model_format']))
                #if file name is empty: call input_directory = data\models\MILESres3.6.txt

        #call (do_read)for reading from a file: call input_directory = data\models\MILESres3.6.txt and format = INTERMEDIATE
        dapathhh = safe_default_input("Please enter the model's folder (Including the Path) ",self.config['model_folder_directory'])
        self.config['model_folder_directory'] = dapathhh
        fulll = ""
        model_files = os.listdir(dapathhh)
        pre_loading_bar(29)
        for mod in model_files:
            if os.name == 'nt':
                fulll = dapathhh + '\\' + mod
                self.model.do_read(fulll,format=self.config['model_format'] , choice = 1)
            else:
                fulll = dapathhh + '/' + mod
                self.model.do_read(fulll,format=self.config['model_format'] , choice = 1)
            sys.stdout.write("#")
        sys.stdout.write("|")
        print("")
        print("")

    def model_read_two(self):
        #call MODEL_FORMATS from pyasad file/set the model default format as INTERMEDIATE
        model_format = safe_default_input(
            'What is the format of your model (' + ', '.join(pyasad.Model.MODEL_FORMATS) + ')',
            self.config['model_format']
        )
        #print error if input not from ['DELGADO', 'GALAXEV', 'MILES', 'INTERMEDIATE']
        while model_format not in pyasad.Model.MODEL_FORMATS:
            error_print('Please enter a valid model format')
            model_format = safe_default_input(
                'What is the format of your model (' + ', '.join(pyasad.Model.MODEL_FORMATS) + ')',
                self.config['model_format']
            )

        #rewrite the model_format to the model we choose
        self.config['model_format'] = model_format
        ok_print("Model format set to {}".format(self.config['model_format']))
                #if file name is empty: call input_directory = data\models\MILESres3.6.txt

        #call (do_read)for reading from a file: call input_directory = data\models\MILESres3.6.txt and format = INTERMEDIATE
        dapathhh = safe_default_input("Please enter the model's folder (Including the Path) ",self.config['model_folder_directory_two'])
        self.config['model_folder_directory_two'] = dapathhh
        fulll = ""
        model_files = os.listdir(dapathhh)
        pre_loading_bar(2)
        for mod in model_files:
            if os.name == 'nt':
                fulll = dapathhh + '\\' + mod
                self.model.do_read(fulll,format=self.config['model_format'] , choice = 1)
            else:
                fulll = dapathhh + '/' + mod
                self.model.do_read(fulll,format=self.config['model_format'] , choice = 1)
            sys.stdout.write("#")
        sys.stdout.write("|")
        print("")
        print("")


    @prompt_command
    def model_age_start_and_step(self):
        		#set (age_start = 0.0)
        self.config['model_age_start'] = safe_default_input(
            'Model Age Start',
            self.config['model_age_start']
        )
        		#set (age_step = 0.2)
        self.config['model_age_step'] = safe_default_input(
            'Model Age Step',
            self.config['model_age_step']
        )
		#call (do_set_age_start) >>> age_start = 0.0
		#call (do_set_age_step) >>> age_step = 0.2
        self.model.do_set_age_start(self.config['model_age_start'])
        self.model.do_set_age_step(self.config['model_age_step'])

    @prompt_command
    def model_interpolation_wavelength_start(self):
        self.config['model_interpolation_wavelength_start'] = self.config['observation_interpolation_wavelength_start']
        self.model.do_interpolation_wavelength_start(
            self.config['model_interpolation_wavelength_start'])
	#set model and obs interpolation_wavelenght_strat equal each other (but i don't have it in default.conf)
	#call (do_interpolation_wavelength_start) >>>

	#call do_interpolation_wavelength_start( interpolation_step = 3.0 , wavelength_start = 3800 )

    @prompt_command
    def model_interpolation_wavelength_start_2(self):
        self.model.do_interpolation_wavelength_start('{} {}'.format(
            self.config['observation_interpolation_step'],
            self.config['observation_wavelength_start']))

    @prompt_command
    def model_interpolation_wavelength_start_no_obsv_smoothed(self):
        obsv = self.observation.values[0]
        self.config['observation_interpolation_step'] = obsv.wavelength_step
        self.model.do_interpolation_wavelength_start('{} {}'.format(
            self.config['observation_interpolation_step'],
            self.config['observation_wavelength_start']))
    #call do_interpolation_wavelength_start( interpolation_step = 3.0,wavelength_start = 3800)

    #set model and obs interpolation_step equal each other
    @prompt_command
    def model_smoothen(self):
        self.config['model_interpolation_step'] = self.config['observation_interpolation_step']
        self.model.do_smoothen(self.config['observation_interpolation_step'])

    @prompt_command
    def model_smoothen_no_obsv_smoothed(self):
        self.config['model_interpolation_step'] = safe_default_input(
            'Model Interpolation Step',
            self.config['model_interpolation_step'])
        self.model.do_smoothen(self.config['model_interpolation_step'])
    #set interpolation_step = 3.0 as a default input
	#call do_smoothen(interpolation_step = 3.0)

    @prompt_command
    def model_wavelength_range(self):
        if self.config['temporary_choice'] == 0:
            choice = self.config['temporary_choice']
            print('Current Wavelength Range: ')
    		#call do_wavelength_index(0,-1): smoothed_MILESres3.6.txt: [3629.0, 3632.0, 3635.0, ..., 6230.0]
            self.model.do_wavelength_index('(0, -1)')
    		#set model_wavelength_start = observation_wavelength_start = 3800
            self.config['model_wavelength_start'] = self.config['observation_wavelength_start']
    		#set model_wavelength_end = observation_wavelength_end = 6230
            self.config['model_wavelength_end'] = self.config['observation_wavelength_end']
    		#call do_set_wavelength_range(3800,6230)
            self.model.do_set_wavelength_range('(%s, %s)' % (
                self.config['observation_wavelength_start'],
                self.config['observation_wavelength_end']))
        else:
            choice = self.config['temporary_choice']
            #print('Current Wavelength Range: ')
    		#call do_wavelength_index(0,-1): smoothed_MILESres3.6.txt: [3629.0, 3632.0, 3635.0, ..., 6230.0]
            self.model.do_wavelength_index('(0, -1)' , choice=1)
    		#set model_wavelength_start = observation_wavelength_start = 3800
            self.config['model_wavelength_start'] = self.config['observation_wavelength_start']
    		#set model_wavelength_end = observation_wavelength_end = 6230
            self.config['model_wavelength_end'] = self.config['observation_wavelength_end']
    		#call do_set_wavelength_range(3800,6230)
            self.model.do_set_wavelength_range('(%s, %s)' % (
                self.config['observation_wavelength_start'],
                self.config['observation_wavelength_end']) , choice=1)

    @prompt_command
    def model_normalize_wavelength(self):
        self.config['model_normalize_wavelength'] = self.config['observation_normalize_wavelength']
        self.model.do_normalize(self.config['model_normalize_wavelength'], self.config['model_input_directory'] , self.config['normalization_norm_choice_number'])
    #set model_normalize_wavelength = observation_normalize_wavelength = 5870
	#call do_normalize(5870)

    @prompt_command
    def model_output(self):
        self.config['model_output_directory'] = safe_default_input(
            'Output directory',
            self.config['model_output_directory'])
        folder_checker(self.config['model_output_directory'])
        self.model.do_write(self.config['model_output_directory'])
    #set model_output_directory = data/models as a default input
	#call do_write(data/models)

    @prompt_command
    def model_output_intermediate(self):
        self.config['model_output_directory'] = safe_default_input(
            'Output directory',
            self.config['model_output_directory'])
        self.model.do_write(self.config['model_output_directory'])
    #set model_output_directory = data/models as a default input
    #call do_write(data/models)

    @prompt_command
    def observation_read(self):
        self.config['observation_input_directory'] = safe_default_input(
            'Enter the Observation file (including the path) ',
            self.config['observation_input_directory'])
        return self.observation.do_read_file_directory(
               self.config['observation_input_directory'])
    # set observation_input_directory = data\observations as a default input
	#call do_read_file_directory(data\observations)

    @prompt_command
    def observation_smoothen(self):
        self.config['observation_interpolation_step'] = safe_default_input(
            'Interpolation Step',
            self.config['observation_interpolation_step'])
        self.observation.do_smoothen(self.config['observation_interpolation_step'])
    #set observation_interpolation_step = 3.0 as a default input
	#call do_smoothen(3.0)

    @prompt_command
    def observation_smoothen_output(self):
        self.config['observation_smoothen_output_directory'] = safe_default_input(
            'Smoothed Output directory',
            self.config['observation_smoothen_output_directory'])
        self.observation.do_write(
            self.config['observation_smoothen_output_directory'],
            prefix='smoothed_')
    #set observation_smoothen_output_directory = data/observations as a default input
	#call do_write(data/observations, prefix='smoothed_' )


    @prompt_command
    def observation_reddening(self):
        		#set observation_reddening_start = 0 as a default input
        self.config['observation_reddening_start'] = safe_default_input(
            'Starting Value for Reddening',
            self.config['observation_reddening_start'])
        		#set observation_reddening_step = 0.01 as a default input
        self.config['observation_reddening_step'] = safe_default_input(
            'Step Size for Reddening',
            self.config['observation_reddening_step'])
        		#set observation_reddening = 0.5 as a default input
        self.config['observation_reddening'] = safe_default_input(
            'Ending Value for Reddening',
            self.config['observation_reddening'])
                #call do_redshift(0, 0.5, 0.01)
        self.observation.do_redshift(' '.join([
            self.config['observation_reddening_start'],
            self.config['observation_reddening'],
            self.config['observation_reddening_step']]))

    @prompt_command
    def observation_wavelength_start(self):
        print('Current Wavelength Range: ')
        		# print ngc1850_sum_d.ascii: [3626.0, 3629.0, 3632.0, ..., 6230.0]
        self.observation.do_wavelength_index('(0, -1)')
        		#set observation_wavelength_start = 3800 as a default input
        self.config['observation_wavelength_start'] = safe_default_input(
            'Starting Wavelength',
            self.config['observation_wavelength_start'])
        		#call do_set_wavelength_start (3800)
        self.observation.do_set_wavelength_start(
            self.config['observation_wavelength_start'])

    @prompt_command
    def observation_wavelength_end(self):
        print('Current Wavelength Range: ')
		# print ngc1850_sum_d.ascii: [3626.0, 3629.0, 3632.0, ..., 6230.0]
        self.observation.do_wavelength_index('(0, -1)')
		#set observation_wavelength_end = 6230 as a default input
        self.config['observation_wavelength_end'] = safe_default_input(
            'Ending Wavelength',
            self.config['observation_wavelength_end'])
        #call do_set_wavelength_end(6230)
        self.observation.do_set_wavelength_end(
            self.config['observation_wavelength_end'])

    @prompt_command
    def observation_wavelength_range(self):
        print('Current Wavelength Range: ')
		#print ngc1850_sum_d.ascii: [3626.0, 3629.0, 3632.0, ..., 6230.0]
		#call do_wavelength_index('(0, -1)')
        self.observation.do_wavelength_index('(0, -1)')
		#set observation_wavelength_start = 3800
		#output:: Wavelength Start (Angstroms) [3800]
        self.config['observation_wavelength_start'] = safe_default_input(
            'Wavelength Start (Angstroms)',
            self.config['observation_wavelength_start'])
		#set observation_wavelength_end = 6230
		#output:: Wavelength End (Angstroms) [6230]
        self.config['observation_wavelength_end'] = safe_default_input(
            'Wavelength End (Angstroms)',
            self.config['observation_wavelength_end'])
		#call do_set_wavelength_range(3800,6230)
        self.observation.do_set_wavelength_range('(%s, %s)' % (
            self.config['observation_wavelength_start'],
            self.config['observation_wavelength_end']))
    #===========================================================================
    @prompt_command
    def observation_normalize_wavelength(self):
        """try:
            if self.config['observation_normalize_wavelength'] != 0:
                ans = 1
            else:
                ans = 2
        except Exception:"""
        if self.config['normalization_norm_choice_number'] == 0:
            ans = 0
            while ans != 1 and ans != 2:
                try:
                    ans = int(safe_default_input("Type '1' for one point normalization , or type '2' for entire range normalization ", self.config['normalization_kind'] ))
                except Exception:
                    print("\t Wrong Input ! Try Again !\n")
            self.config['normalization_norm_choice_number'] = ans
            self.config['normalization_kind'] = ans
            if ans == 1:
                self.config['observation_normalize_wavelength'] = safe_default_input(
                    'At which value of Wavelength (Angstroms) do you want to normalize',
                    self.config['observation_normalize_wavelength'])
                self.observation.do_normalize(self.config['observation_normalize_wavelength'], self.config['observation_filename'] , int(self.config['normalization_norm_choice_number']))
            else:
                self.config['observation_normalize_wavelength'] = "All"
                self.observation.do_normalize(self.config['observation_normalize_wavelength'], str(self.config['observation_filename']) , int(self.config['normalization_norm_choice_number']))
        else:
            if ans == 1:
                self.config['observation_normalize_wavelength'] = safe_default_input(
                    'Wavelength (Angstroms)',
                    self.config['observation_normalize_wavelength'])
                self.observation.do_normalize(self.config['observation_normalize_wavelength'], self.config['observation_filename'] , int(self.config['normalization_norm_choice_number']))
            else:
                results_list = []
                self.config['observation_normalize_wavelength'] = "All"
                results_list.append( self.observation.do_normalize(self.config['observation_normalize_wavelength'], str(self.config['observation_filename']) , int(self.config['normalization_norm_choice_number'])) )
                print(results_list)
    #set observation_normalize_wavelength = 5870 as a default input
	#output:: Wavelength (Angstroms) [5870]
	#call do_normalize(5870)

    @prompt_command
    def observation_output(self):
        self.config['observation_output_directory'] = safe_default_input(
            'Output directory',
            self.config['observation_output_directory'])
        folder_checker(self.config['observation_output_directory'])
        self.observation.do_write(
            self.config['observation_output_directory'],
            prefix='normalized_')
    #set observation_output_directory = data/observations as a default input
	#output:: Output directory [data/observations]
	#call do_write(data/observations, prefix='normalized_')

    def object_generate(self):
        print('Generating Reddening/Ages files...')
        for model in self.model.values:
            for obsv in self.observation.values:
                obj = pyasad.Asad.from_observation_model(obsv, model)
                self.object.values.append(obj)                        #append obj to the values
                ok_print('Done. Model: %s Observation: %s' % \
                         (model.name, obsv.name))
    #output::Generating Reddening/Ages files...
	#two loops (model.vales (obs.values()))
	#call from_observation_model((observation, model)) from pyasad.Asad:
    #ourput:: Done. Model: model.name Observation: obsv.name

    #function that sorts itemzzz in temporary folders
    def object_sorter(self , directory):
        import shutil
        global observation_counter
        all_files = os.listdir(directory)
        #print(all_files)
        strr = ""
        fdirectory = ""
        flist = []
        for i in self.observation.values:
            strr = i.name
            if os.name == 'nt':
                fdirectory = directory + "\\" + strr[:strr.rfind(".")]
                #fdirectroy.replace("\\","/")
                #print(fdirectory)
                os.makedirs(fdirectory)
            elif os.name != 'nt':
                fdirectory = directory + "/" + strr[:strr.rfind(".")]
                os.makedirs(fdirectory)
            for file in all_files:
                if file.find(strr) != -1:
                    if os.name == 'nt':
                        shutil.move(directory + "\\" +file , fdirectory)
                    else:
                        shutil.move(directory + "/" +file , fdirectory)
            flist.append(fdirectory)
        return flist




    def object_output(self , choice):
        if choice == 0:
            self.config['object_output_directory'] = safe_default_input(
                'Output directory',
                self.config['object_output_directory'])
            self.config['object_temp_path'] = self.config['object_output_directory']
            #print("\nPlease Wait...\n")
            self.config['object_msp_plot_dir'] = self.config['object_output_directory']
            folder_checker(self.config['object_output_directory'])
            self.object.do_write(self.config['object_output_directory'])
            return self.object_sorter(self.config['object_output_directory'])

        else:
            #46555
            print("\nPlease Wait...\n")
            #self.config['object_output_directory'] = self.config['object_temp_path']
            self.config['object_msp_plot_dir'] = self.config['object_temp_path']
            self.object.do_write(self.config['object_temp_path'],choice = 1)
            return self.object_sorter(self.config['object_temp_path'])
    #set object_output_directory = data/objects as a default input
	#output:: Reddening/Ages directory [data/objects]
	#call do_write (data/objects)

    def object_calculate_chosen(self,choice=0):
        if choice == 0:
            #output:: Statistic (chi-squared, ks)[chi-squared] and set it as a default input
            stat_test = safe_default_input(
                'What Statistical method you want to use (' + ', '.join(pyasad.Statistics.STAT_TEST_NAMES) + ')',
                self.config['object_test_statistic']
            )
            #if not from (chi-squared, ks): print error and rewrite the default
            while stat_test not in pyasad.Statistics.STAT_TEST_NAMES:
                error_print("Invalid statistic chosen, please choose a valid statistic from the list below")
                stat_test = safe_default_input(
                     'What Statistical method you want to use (' + ', '.join(pyasad.Statistics.STAT_TEST_NAMES) + ')',
                     self.config['object_test_statistic'] , choice
                )
            self.config['object_test_statistic'] = stat_test
            print('\nCalculating best match of age and reddening ({})...\n'.format(
                self.config['object_test_statistic']))
            self.object.do_calculate_chosen_model(self.config['object_test_statistic'])
        else:
            #output:: Statistic (chi-squared, ks)[chi-squared] and set it as a default input
            stat_test = "Chi-squared minimization"
            self.object.do_calculate_chosen_model(self.config['object_test_statistic'],choice=1)
        #output:: Calculating best match of age and reddening (chi-squared)...
    	#call do_calculate_chosen_model(chi-squared)


    @prompt_command
    def object_output_chosen(self):
        self.config['object_chosen_directory'] = safe_default_input(
            'Output file or directory',
            self.config['object_chosen_directory'])
        folder_checker(self.config['object_chosen_directory'])
        self.config['plot_surface_dir'] = self.object.do_write_chosen(self.config['object_chosen_directory'],
                                    self.config)
        self.fpath = self.config['plot_surface_dir']
        #print(self.fpath)
        #print(self.config['plot_surface_dir'])
        #print(fpath)

        #return str(self.fpath)
    # set object_chosen_directory = data\results as a default input
	#output:: Output file or directory [data\results]
	#call do_write_chosen(data\results, self.config)

    @prompt_command
    def plot_output_format(self):
        self.config['plot_output_format'] = safe_default_input(
            'Plot output format',
            self.config['plot_output_format'])
    #set plot_output_format = eps as a default input
	#output::Plot output format [eps]

    @prompt_command
    def plot_model_title(self):
        self.config['plot_model_title'] = safe_default_input(
            'Custom model title',
            self.config['plot_model_title'])
    #set plot_model_title = Model as a default input
	#output:: Custom model title [Model]

    def plot_surface_output_msp(self,multi_msp_result,multi_,folder):
        #print("OK_MSP")
        _path_ = ''
        _path = ''
        path_ = ''

        self.plot_output_format()
        self.config['plot_surface_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_surface_directory'])

        title = None
        if parse_input_yn('Custom plot title'):
            title = safe_default_input('Plot title', None)

        folder_checker(self.config['plot_surface_directory'])
        for u in folder:
            self.config['choices_output_surface_plots'] = 'Y'
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                arrr = os.listdir(u)
                #print(arrr)
                for _a in arrr:
                    if _a.find("msp") == -1:
                        arrr.remove(_a)

                indexer = 0
                print('\n Plotting the surface plot...\n')
                for _a in arrr:
                    #print(arrr)
                    new_ele = ""
                    if multi_:
                        for res in multi_msp_result[folder.index(u)]:
                            if os.name == 'nt':
                                new_ele = res[res.rfind("\\")+1:]
                            elif os.name != 'nt':
                                new_ele = res[res.rfind("/")+1:]
                            if _a == new_ele:
                                try:
                                    _path = str(u)
                                    path_ = str(_a)
                                    if os.name == 'nt':
                                        _path_ = _path + '\\' + path_
                                    elif os.name == 'mac' or os.name == 'posix':
                                        _path_ = _path + '/' + path_

                                    file_name = main_plotter(_path_, self.config['plot_output_format'], title , self.config['plot_surface_directory'])
                                    ok_print('\nSaved < ' + file_name + ' > to ' + str(self.config['plot_surface_directory']))
                                except Exception as e:
                                    print("@ Error: " + str(e) )
                    else:
                        try:
                            _path = str(u)
                            path_ = str(_a)
                            if os.name == 'nt':
                                _path_ = _path + '\\' + path_
                            elif os.name == 'mac' or os.name == 'posix':
                                _path_ = _path + '/' + path_

                            file_name = main_plotter(_path_, self.config['plot_output_format'], title , self.config['plot_surface_directory'])
                            ok_print('\nSaved < ' + file_name + ' > to ' + str(self.config['plot_surface_directory']))
                        except Exception as e:
                            print("@ Error: " + str(e) )


    @prompt_command
    def plot_surface_output(self):
        #print("OK_NORMAL")
        self.plot_output_format()
        self.config['plot_surface_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_surface_directory'])

        title = None
        if parse_input_yn('Custom plot title'):
            title = safe_default_input('Plot title', None)

        self.object.do_plot_surface(self.config['plot_surface_directory'],
                                    format=self.config['plot_output_format'], title=title)

    @prompt_command
    def plot_scatter_output(self):
		#set plot_scatter_directory = data\Results as a default input
		#output:: Output directory = data\Results
        self.config['plot_scatter_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_scatter_directory'])
        reddenings, ages = [], []
        #if print (Custom age and reddening pairs?) is Y: ages (call safe_input) print (Ages:),
		#reddenings (call reddenings) print (Reddenings: )
        if parse_input_yn('Custom age and reddening pairs?'):
            ages = [float(a) for a in safe_input('Ages: ').split(' ')]
            reddenings = [float(r) for r in safe_input('Reddenings: ').split(' ')]

        title = None
        #if print (Custom plot title): output:: Plot title [None]: and set it to default
        if parse_input_yn('Custom plot title'):
            title = safe_default_input('Plot title', None)

        #call do_plot_scatter(data\Results, ages, reddenings, format = eps|| pdf , title )
        self.object.do_plot_scatter(self.config['plot_scatter_directory'],
                                    ages=ages, reddenings=reddenings,
                                    format=self.config['plot_output_format'], title=title)

    @prompt_command
    def plot_scatter_output_aux(self):
        self.config['plot_scatter_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_scatter_directory'])

        #set plot_scatter_directory = data\Results as a default input
		#output:: Output directory = data\Results
        title = None
        #if print (Custom plot title) is Y: output:: Plot title [None]: and set it to default
        if parse_input_yn('Custom plot title'):
            title = safe_default_input('Plot title', None)

        reddenings, ages = [], []
        #call do_plot_scatter(data\Results, ages, reddenings, format = eps|| pdf , title )
        self.object.do_plot_scatter(self.config['plot_scatter_directory'],
                                    ages=ages, reddenings=reddenings,
                                    format=self.config['plot_output_format'], title=title)

    @prompt_command
    def plot_residual_output(self):
        # set plot_residual_directory = data/plots as a default input
		#output:: Output directory = data/plots
        self.config['plot_residual_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_residual_directory'])

        title = None
        #if print (Custom plot title) is Y :output:: Plot title [None]: and set it to default
        if parse_input_yn('Custom plot title'):
            title = safe_default_input('Plot title', None)

        #call do_plot_residual(data/plots, format, title)
        self.object.do_plot_residual(self.config['plot_residual_directory'],
                                     format=self.config['plot_output_format'], title=title)


    def plot_residual_match_output(self, twoModels,chi_result=[],choice=0):
        #set plot_residual_match_directory = data\results as a default input
		#Output directory = data\results
        self.config['plot_residual_match_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_residual_match_directory'])

        title = None
        #if print (Custom plot title) is Y :output:: Plot title [None]: and set it to default
        if parse_input_yn('Custom plot title'):
            title = safe_default_input('Plot title', None)

        #call do_plot_residual_match(data\results, format, title)
        key = False
        if parse_input_yn('Custom plot keys'):
            key = True
        folder_checker(self.config['plot_residual_match_directory'])
        self.object.do_plot_residual_match(twoModels,
            self.config['plot_residual_match_directory'],
            format=self.config['plot_output_format'], title=title ,chi_result=chi_result,key=key)

    @prompt_command
    def plot_surface_error_output(self):
        self.config['plot_surface_error_directory'] = safe_default_input(
            'Output directory',
            self.config['plot_surface_error_directory'])
        self.object.do_plot_surface_error(self.config['plot_surface_error_directory'],
                                          format=self.config['plot_output_format'])
    #set plot_surface_error_directory = data/plots as a default input
	#Output directory = data/plots
	#call do_plot_surface_error(data/plots, format)

    @prompt_command
    def plot_scatter_tile_output(self):
        self.object.do_plot_scatter_tile(self.config['plot_scatter_tile_directory'],
                                         format=self.config['plot_output_format'])
    #call do_plot_scatter_tile(plot_scatter_tile_directory = ???? not exists, format)
    @prompt_command
    def plot_surface_tile_output(self):
        self.object.do_plot_surface_tile(self.config['plot_surface_tile_directory'],
                                         format=self.config['plot_output_format'])

    def dir_finder(self , keyword):#_this function allows for slicing the string so that the temp file for output reddning age can be generated.
        """if os.path.isdir(path):
            return path
        if os.path.isfile(path):
            if os.name == 'nt':
                return path[:path.rfind("\\")]
            elif os.name == 'mac' or os.name == 'posix':
                return path[:path.rfind("/")]"""
        if os.name == 'nt':
            working_path = os.getcwd()
            working_path = working_path + '\\' + 'data' + '\\' + keyword
            #caches = os.listdir(working_path)
            #for f in caches:
            #    os.remove(working_path + '\\' + f)
        elif os.name == 'mac' or os.name == 'posix':
            working_path = os.getcwd()
            working_path = working_path + '/' + 'data' + '/' + keyword
        return working_path



	#call do_plot_surface_tile (plot_surface_tile_directory = data/plots, format )

#setting screen commands and calling the functions (main function)
    def cmdloop(self):
        #error_print("\t Attention ! This version of the program is BETA (2.4). Bugs and errors are still expected in this version. \n Please Note that the entire range normalization is not working temporarly \n    Press ENTER to start this program ---->")
        #zzzw = raw_input('\n')
        twoModels = False
        observation_is_smoothed = False
        msp_chosen = False
        multi_ = False
        print("")
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
        else:
            working_path = os.getcwd()
            working_path = working_path + '/' + 'data' + '/' + 'temp'
            caches = os.listdir(working_path)
            for f in caches:
                try:
                    os.remove(working_path + '/' + f)
                except Exception:
                    shutil.rmtree(working_path + '/' + f)
        info_print("      ASAD: Analyzer of Spectra for Age Determination")
        #info_print("Assistant mode.")
        info_print("----Press ENTER key to choose the pre-set Default Options----");   #Informs user that ENTER key chooses the default option.
        self.config['object_temp_path_ndx'] == -1
        self.observation_read()
        #print (observ_fname)
        self.config['observation_filename'] = self.config['observation_input_directory']
        self.config['object_temp_path'] = self.dir_finder('temp')
        #print (self.config['observation_filename'])
        #print(observation_counter)
        if parse_input_yn('Would you like to use the analysis made on the observation in the previous run', default = False):
            self.previousAnalysisObservation()
            """if parse_yn(self.config['choices_smooth_observation']):
                observation_is_smoothed = True"""
        else:
            if parse_input_yn('Do you want to chose the wavelength range of the observation', default=True):
                #if parse_input_yn('Start of the range of the observation wavelength ', default=True):
                self.observation_wavelength_start()
                #if parse_input_yn('End of the range of the observation wavelength ', default=True):
                self.observation_wavelength_end()
                self.config['choices_smooth_observation'] = 'N'
            #"""if parse_input_yn('Observation set wavelength start (Angstroms)', default=True):
            #    self.observation_wavelength_start()
            #if parse_input_yn('Smooth the observation', default=False):
            #    self.config['choices_smooth_observation'] = 'Y'
            #    self.observation_smoothen()
            #    observation_is_smoothed = True"""
            else:
                self.config['choices_smooth_observation'] = 'N'
                """
            if parse_input_yn('Output smoothed observations'):
                self.config['choices_output_smoothed_observation'] = 'Y'
                self.observation_smoothen_output()

            else:"""
        self.config['choices_output_smoothed_observation'] = 'N'
        if parse_input_yn('Do you want to apply reddening correction to the observation', default=False): #Reddening Correction Default set to No.
            self.config['choices_reddening_correction'] = 'Y'
            self.observation_reddening()
        else:
            self.config['choices_reddening_correction'] = 'N'

        if parse_input_yn('Do you want to normalize the observation', default=True):
            self.config['choices_normalize_wavelength'] = 'Y'
            self.config['normalization_norm_choice_number'] = 0
            self.observation_normalize_wavelength()
        else:
            self.config['choices_normalize_wavelength'] = 'N'
        if parse_input_yn('Do you want to output the new observation file'):
            self.config['choices_output_observation'] = 'Y'
            self.observation_output()
        else:
             self.config['choices_output_observation'] = 'N'

        self.update_config()


        ok_print("Comparing model (without combination) with the observation")
        mchoice = 3
        #mchoice == 1
        model_folder = False
        lendx = 0
        while lendx == 0:
            try:
                mchoice = int( safe_default_input(" Please enter '1' to input a single model, or enter '2' to enter a folder of models [MG models only] ---> ",self.config['choices_model_menu_one']) )
                lendx = 1
            except:
                print("\tWrong Input ! Please try again !")

        original_model_input = ""
        if mchoice == 1:
            self.model_read()
            original_model_input = self.config["model_input_directory"]
        elif mchoice == 2:
            lendx = 0
            mmchoice = 0
            while lendx == 0:
                try:
                    mmchoice = int( safe_default_input("\n\tPlease enter '1' to input a single MG model folder, or enter '2' to enter all ages MG model folder---> ",self.config['choices_model_menu_two']) )
                    lendx = 1
                except:
                    print("\tWrong Input ! Please try again !")
            if mmchoice == 1:
                self.model_read_two()
            else:
                self.model_read_folder()
            model_folder = True
            #original_model_input = self.config['model_folder_directory']




        potential_msp = False
        import random
        random_number = random.randint(1,99999)

        num = 0
        if model_folder == False:
            if parse_input_yn('Would you like to generate the MG file',default=True) != False:
                self.config['choices_object_output'] = 1
                num = int(self.config['choices_object_output'])
                msp_chosen = True
                multi_ = False
                not_all_confirmer = parse_input_yn("Input the age for MG ", default=False)
                if not_all_confirmer == True:

                    print("\n\tComparing model (with combination) to the observation...\n")
                    column,inputAge = fg.getColumn(0.0) #Getting the column and input age from FileGenFunctions

                    if os.name == 'nt':
                        self.config['model_msp_output'] = "data\\models"
                    else:
                        self.config['model_msp_output'] = "data/models"


                    calcFileName = fg.calculateFirstColumns( self.config['model_input_directory'] , column ,inputAge , self.config['model_msp_output'] , 0 ,random_number=random_number)

                    print("\nAlmost there...\n")
                    #print(calcFileName[0])
                    self.model_read(calcFileName[0] , 1)

                    twoModels = True
                else:
                    #self.config['model_msp_output'] = safe_default_input("\nEnter your MG file's location " , self.config['model_msp_output'] )
                    #filezzz = os.listdir("C:\Users\hicha\Desktop\ASAD_2.3_BETA\data\MSP")
                    if os.name == 'nt':
                        self.config['model_msp_output'] = "data\\models"
                    else:
                        self.config['model_msp_output'] = "data/models"
                    filezzz = []
                    print("")
                    ok_print(" Generating MG files from 6.8 to 9.5 ...")
                    print("")
                    print ("|" + (" " * (28*2)) + "|")
                    print("")
                    sys.stdout.write("|")
                    for i in xrange(68,96):
                        i = float(i)
                        i /= 10
                        column,inputAge = fg.getColumn(i,1) #Getting the column and input age from FileGenFunctions
                        sys.stdout.write("#")
                        calcFileName = fg.calculateFirstColumns( self.config['model_input_directory'] , column ,inputAge , self.config['model_msp_output'] , 0 ,printer=1,random_number=random_number)
                        sys.stdout.write("#")
                        #ok_print("Enter the name of the generated file as input")
                        #print("\nAlmost there...\n")
                        filezzz.append(calcFileName[0])
                    for file in filezzz:
                        self.model_read(file , 1)
                    twoModels = True
                    multi_ = True
                    sys.stdout.write("|")
                    print("")
                    print("")

        else:
            twoModels = True
            potential_msp = True
            msp_chosen = True
            if mmchoice == 2:
                multi_ = True


                #chi_square_minimization(self.config['model_msp_output'])
            #self.config['temporary__string'] = self.config['observation_input_directory']
            #self.config['model_temp_filename']


        if parse_input_yn('Would you like to use the previous analysis made on the model',default = False):
            self.previousAnalysisModel()
        else:

            if parse_input_yn('Do you want to create a header with the ages for the model file'):
                self.config['choices_set_age_start_and_step'] = 'Y'
                self.model_age_start_and_step()
            else:
                self.config['choices_set_age_start_and_step'] = 'N'

            #if observation_is_smoothed:
            #    self.model_interpolation_wavelength_start_2()
            #    self.model_smoothen()
            #else:
                #if parse_input_yn('Smooth the model', default=False):   #Smooth the model Default set to No.
                    #self.config['choices_smooth_model'] = 'Y'
                    #self.model_interpolation_wavelength_start_no_obsv_smoothed()
                    #self.model_smoothen_no_obsv_smoothed()
                #else:
        self.config['choices_smooth_model'] = 'N'
        self.config['object_temp_path'] = self.dir_finder('temp')
            #13222
        self.model_wavelength_range()
        self.model_normalize_wavelength()

        if msp_chosen and mchoice == 1:
            self.config["model_input_directory"] = original_model_input
        self.update_config()

        self.object_generate()
        multi_msp_result = []
        self.config['object_temp_path_ndx'] = 0
        if parse_input_yn('Do you want to output the new model file'):
            self.config['choices_output_models'] = 'Y'
            self.model_output()
        else:
            self.config['choices_output_models'] = 'N'
        self.config['model_filename_redd'] = ''
        multiii = []
        c = 0
        if parse_input_yn('Do you want to output the file that has the observation and the models'):
            self.config['choices_output_reddening_age_files'] = 'Y'
            multiii = self.object_output(0)

            if multi_ == True:
                for u in multiii:
                    multi_msp_result.append(chi_square_minimization(u,self.config['object_output_directory'],self.observation.values[c].name))
                    c = c + 1
                self.object_calculate_chosen(1)
                if parse_input_yn('Output best Reddening/Age match of MG', default= False):
                    output_dirr = safe_default_input('Output file or directory',self.config['object_chosen_directory'])
                    folder_checker(output_dirr)
                    list_tempp = os.listdir(self.config['object_temp_path'])
                    for ele in list_tempp:
                        if os.name =='nt':
                            if ele.find("chi_sq_output") != -1:
                                shutil.move(self.config['object_temp_path'] + '\\' + ele , output_dirr)
                                ok_print("Best Reddening/Age match is saved to " + output_dirr + " as " + ele + "\n")
                        else:
                            if ele.find("chi_sq_output") != -1:
                                shutil.move(self.config['object_temp_path'] + '/' + ele , output_dirr)
                                ok_print("Best Reddening/Age match is saved to " + output_dirr + " as " + ele + "\n")

            else:
                self.config['temporary_choice'] = num
                #print(self.config['temporary_choice'])
                self.object_calculate_chosen(0)

                if parse_input_yn('Output best Reddening/Age match', default= False):
                    self.config['choices_output_best_reddening_age_match'] = 'Y'
                    self.object_output_chosen()
                else:
                    self.config['choices_output_best_reddening_age_match'] = 'N'
        else:
            self.config['choices_output_reddening_age_files'] = 'N'
            if msp_chosen:
                multiii = self.object_output(1)
                if multi_:
                    #print(self.values[0].observation.original_name)
                    #print(self.values[1].observation.original_name)
                    for u in multiii:
                        multi_msp_result.append(chi_square_minimization(u,self.config['object_temp_path'],self.observation.values[c].name))
                        c = c + 1
                    self.object_calculate_chosen(1)
                    if parse_input_yn('Output best Reddening/Age match for MG', default= True):
                        output_dirr = safe_default_input('Output file or directory',self.config['object_chosen_directory'])
                        folder_checker(output_dirr)
                        list_tempp = os.listdir(self.config['object_temp_path'])
                        for ele in list_tempp:
                            if os.name =='nt':
                                if ele.find("chi_sq_output") != -1:
                                    #os.rename()
                                    shutil.move(self.config['object_temp_path'] + '\\' + ele , output_dirr)
                                    ok_print("Best Reddening/Age match is saved to " + output_dirr + " as " + ele + "\n")
                            else:
                                if ele.find("chi_sq_output") != -1:
                                    shutil.move(self.config['object_temp_path'] + '/' + ele , output_dirr)
                                    ok_print("Best Reddening/Age match is saved to " + output_dirr + " as " + ele + "\n")
                else:
                    self.config['temporary_choice'] = num
                    #print(self.config['temporary_choice'])
                    self.object_calculate_chosen(0)

                    if parse_input_yn('Output best Reddening/Age match', default= True):
                        self.config['choices_output_best_reddening_age_match'] = 'Y'
                        self.object_output_chosen()
                    else:
                        self.config['choices_output_best_reddening_age_match'] = 'N'
            else:
                self.config['temporary_choice'] = num
                #print(self.config['temporary_choice'])
                self.object_calculate_chosen()

                if parse_input_yn('Output best Reddening/Age match', default= True):
                    self.config['choices_output_best_reddening_age_match'] = 'Y'
                    self.object_output_chosen()
                else:
                    self.config['choices_output_best_reddening_age_match'] = 'N'
            #self.object_output(1)
            #self.object_output_chosen()
        #print(">>>>>>>>>>>>" + self.config['plot_surface_dir'])
        #????!!!!"""

        #Plots Start Here
        #print(multiii)

        if parse_input_yn('Output residual plots', default=True):
            self.plot_output_format()
            self.config['choices_output_residual_plots'] = 'Y'
            if multi_:
                self.plot_residual_match_output(twoModels,chi_result = multi_msp_result , choice=1 )
            else:
                self.plot_residual_match_output(twoModels,chi_result = multi_msp_result, choice=0 )
        else:
            self.config['choices_output_residual_plots'] = 'N'
        self.config['temporary_choice'] = num
        #print(self.config['temporary_choice'])
        if msp_chosen:
            if parse_input_yn('Output MG surface plots', default=True):
                self.config['choices_output_surface_plots'] = 'Y'
                self.config['object_output_directory'] = self.config['object_temp_path']
                self.plot_surface_output_msp(multi_msp_result,multi_,multiii)
            else:
                self.config['choices_output_surface_plots'] = 'N'
        else:
            if parse_input_yn('Output surface plots', default=True):
                self.config['choices_output_surface_plots'] = 'Y'
                self.plot_surface_output()
            else:
                self.config['choices_output_surface_plots'] = 'N'
         #New Update 7/12/2018
        """if parse_input_yn('Output best spectra match plots', default=True):
            self.config['choices_output_best_spectra_match_plots'] = 'Y'
            self.plot_scatter_output()
        else:
            self.config['choices_output_best_spectra_match_plots'] = 'N'
"""
        info_print("\t Thank you for using ASAD ! Terminating Program...")

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
    ##        if parse_input_yn('Output detailed residual plots', default=False): #Output detailed residual plots set to No.
    ##            self.config['choices_output_detailed_residual_plots'] = 'Y'
    ##            self.plot_residual_output()
    ##        else:
    ##            self.config['choices_output_detailed_residual_plots'] = 'N'
    ##        if parse_input_yn('Output surface tile plot', default=False):   #Output surface tile plot set to No.
    ##            self.config['choices_output_surface_title_plot'] = 'Y'
    ##            self.plot_surface_tile_output()
    ##        else:
    ##            self.config['choices_output_surface_title_plot'] = 'N'

            self.update_config()

#==============================================================================

class Main_Shell(cmd.Cmd):
    intro = "Welcome. Type ? for help."
    prompt = "<pyasad> "

    def __init__(self, *args, **kwargs):
        self._object = Object_Shell()
        cmd.Cmd.__init__(self, *args, **kwargs)

    def execute(self, path):
        "Execute a command script"
        with io.open(os.path.abspath(path), 'r') as f:
            for line in f.readlines():
                if line.lstrip(' ').startswith('#'):
                    pass
                else:
                    self.onecmd(line)

    def emptyline(self):
        pass

    @property
    def base(self):
        return self.object._base
    @property
    def model(self):
        return self.object._model
    @property
    def observation(self):
        return self.object._observation

    @property
    def object(self):
        return self._object
    @object.setter
    def object(self, obj):
        self._object = obj

    def do_base(self, arg):
        return self.base.onecmd(arg)
    def do_model(self, arg):
        return self.model.onecmd(arg)
    def do_observation(self, arg):
        return self.observation.onecmd(arg)
    def do_object(self, arg):
        return self.object.onecmd(arg)
    def do_run(self, arg):
        return Run_Shell().cmdloop()
    def do_quit(self, arg):
        print('Quitting')
        sys.exit(0)

#==============================================================================

def override_safe_default_input(s, default=None):
    return default

def override_prompt_command(func):
    return func

def set_not_interactive():
    global safe_default_input
    safe_default_input = override_safe_default_input

#===============================================================================
