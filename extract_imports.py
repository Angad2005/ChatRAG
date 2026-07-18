import os
import re
import sys
import subprocess
import json

def extract_imports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    # Remove comments and strings to avoid false positives
    # Remove single line comments
    content = re.sub(r'#.*', '', content)
    # Remove triple quoted strings (both single and double)
    content = re.sub(r'\'\'\'[\s\S]*?\'\'\'', '', content)
    content = re.sub(r'\"\"\"[\s\S]*?\"\"\"', '', content)
    # Find import statements
    imports = re.findall(r'^\s*import\s+(.+)$', content, re.MULTILINE)
    from_imports = re.findall(r'^\s*from\s+(\S+)\s+import', content, re.MULTILINE)
    modules = set()
    for imp in imports:
        # Handle multiple imports: import os, sys
        for module in imp.split(','):
            module = module.strip().split()[0]  # Remove 'as' alias
            if module:
                modules.add(module)
    for module in from_imports:
        # Get top-level package
        top_level = module.split('.')[0]
        modules.add(top_level)
    return modules

def is_stdlib(module):
    # Check if module is in standard library
    if hasattr(sys, 'stdlib_module_list'):
        return module in sys.stdlib_module_list
    elif hasattr(sys, 'stdlib_module_names'):
        return module in sys.stdlib_module_names
    else:
        # Fallback: try to import it; if it's built-in, it's stdlib
        # But we don't want to actually import because it might have side effects.
        # Instead, use a list of known stdlib modules from Python 3.10
        # This is not exhaustive but should cover most cases.
        stdlib_modules = {
            'argparse', 'array', 'ast', 'asyncio', 'base64', 'bisect', 'calendar', 'cmath', 'cmd', 'code',
            'codecs', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser', 'contextlib',
            'contextvars', 'copy', 'csv', 'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal',
            'difflib', 'dis', 'distutils', 'doctest', 'email', 'encodings', 'enum', 'errno', 'faulthandler',
            'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'fractions', 'ftplib', 'functools', 'gc', 'getopt',
            'getpass', 'gettext', 'glob', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib',
            'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3', 'linecache',
            'locale', 'logging', 'lzma', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap',
            'modulefinder', 'msilib', 'msvcrt', 'multiprocessing', 'netrc', 'nis', 'nntplib', 'numbers',
            'operator', 'optparse', 'os', 'ossaudiodev', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes',
            'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'pprint', 'profile', 'pstats', 'pty', 'pwd',
            'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline', 'reprlib',
            'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex',
            'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd',
            'sqlite3', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau',
            'symbol', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile',
            'termios', 'test', 'textwrap', 'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize',
            'trace', 'traceback', 'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing', 'unicodedata',
            'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg',
            'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zoneinfo'
        }
        return module in stdlib_modules

def main():
    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    all_modules = set()
    for file in py_files:
        modules = extract_imports(file)
        all_modules.update(modules)
    # Filter out standard library modules
    external_modules = [m for m in all_modules if not is_stdlib(m) and not m.startswith('_')]
    # Sort and print
    for module in sorted(external_modules):
        print(module)

if __name__ == '__main__':
    main()