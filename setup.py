from distutils.core import setup

setup(name="asad",
      author='Sami Abdin',
      version="0.11",
      packages=['asad'],
      requires=['colorama', 'matplotlib', 'PySide', 'numpy'],
      scripts=['asad.py']
      )
