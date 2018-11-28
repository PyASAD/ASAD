from cx_Freeze import setup, Executable

buildOptions = dict(
    packages = ["numpy", "matplotlib", "colorama"],
    excludes = [
        "docutils",
        "setuptools",
        "pytz",
        "multiprocessing",
        "IPython",
        "importlib",
        "email",
        "compiler",
        "lib2to3",
        "markupsafe",
        "zmq",
        "scipy",
        "sqlite3",
        "Tkinter",
        "jinja2",
        "OpenGL",
        "pydoc_data",
        "nose",
        "pygments",
        "sphinx",
        "tornado",
        "win32com",
        "xml",
        "collections.sys",
	"collections._weakref",
    ],
    bin_path_excludes=[
        "/Library/Frameworks/Tcl.framework",
        "/Library/Frameworks/Tk.framework"
    ],
    optimize=2,
    create_shared_zip=True,
    compressed = True,
    include_msvcr=True,
    silent=True
    )

base = 'Console'

executables = [
    Executable('asad.py', base=base)
]

setup(name='asad',
      author='Sami Abdin',
      version='0.11',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)
