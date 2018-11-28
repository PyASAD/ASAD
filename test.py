"""import asad.pyasad as pa
a = pa.Model(path='data/models/MILES.txt', format='MILES')
print(a.format())"""
import shutil as computer
#computer.copyfile("C:\\Users\\hicha\\Desktop\\ASAD\\default.conf","C:\\Users\\hicha\\Desktop\\ASAD\\default.txt")
import os
if os.name == 'nt':
    before_copy = str(os.getcwd()) + '\\' + 'default.conf'
else:
    before_copy = str(os.getcwd()) + '/' + 'default.conf'

after_copy = before_copy
print after_copy
after_copy.replace("default.conf","default.txt")
print after_copy
try:
    computer.copyfile(before_copy,after_copy)
except Exception as e:
    print "@ ERROR ! " + str(e)
