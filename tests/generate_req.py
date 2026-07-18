import os
import re
import subprocess
import sys

def extract_imports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    # Remove comments and strings to avoid false positives
    # Remove single line comments
    content = re.sub(r'#.*', '', content)
    # Remove triple quoted strings (both single and double quotes)
    content = re.sub(r'\'\'\'[\s\S]*?\'\'\'', '', content)
    content = re.sub(r'\"\"\"[\s\S]*?\"\"\"', '', content)
    # Find import statements
    imports = re.findall(r'^\s*import\s+(.+)$', content, re.MULTILINE)
    from_imports = re.findall(r'^\s*from\s+(\S+)\s+import', content, re.MULTILINE)
    modules = set()
    for imp in imports:
        # Handle multiple imports on one line: import os, sys
        for module in imp.split(','):
            module = module.strip().split()[0]  # Remove any 'as' alias
            if module:
                modules.add(module)
    for module in from_imports:
        # Get the top-level package
        top_level = module.split('.')[0]
        modules.add(top_level)
    return modules

def is_stdlib_module(module_name):
    # Check if the module is a built-in or standard library module
    if hasattr(sys, 'stdlib_module_list'):
        return module_name in sys.stdlib_module_list
    elif hasattr(sys, 'stdlib_module_names'):
        return module_name in sys.stdlib_module_names
    else:
        # Fallback: check if it's a built-in module or in a list of common stdlib modules
        builtin = set(sys.builtin_module_names)
        common_stdlib = {
            'os', 'sys', 're', 'json', 'csv', 'math', 'collections', 'itertools', 'functools',
            'heapq', 'bisect', 'array', 'weakref', 'types', 'copy', 'pprint', 'reprlib',
            'enum', 'numbers', 'decimal', 'fractions', 'random', 'secrets', 'statistics',
            'datetime', 'zoneinfo', 'calendar', 'collections', 'array', 'weakref', 'types',
            'copy', 'pprint', 'reprlib', 'enum', 'numbers', 'cmath', 'decimal', 'fractions',
            'random', 'secrets', 'statistics', 'itertools', 'collections', 'array', 'weakref',
            'types', 'copy', 'pprint', 'reprlib', 'enum', 'numbers', 'cmath', 'decimal',
            'fractions', 'random', 'secrets', 'statistics', 'itertools', 'collections', 'array',
            'weakref', 'types', 'copy', 'pprint', 'reprlib', 'enum', 'numbers', 'cmath', 'decimal',
            'fractions', 'random', 'secrets', 'statistics', 'itertools', 'collections', 'array',
            'weakref', 'types', 'copy', 'pprint', 'reprlib', 'enum', 'numbers', 'cmath', 'decimal',
            'fractions', 'random', 'secrets', 'statistics'
        }
        return module_name in builtin or module_name in common_stdlib

def is_local_module(module_name, directory='.'):
    # Check if there is a .py file with this name in the directory (or directory/package)
    # Check for file.py
    if os.path.exists(os.path.join(directory, f"{module_name}.py")):
        return True
    # Check for package/__init__.py
    if os.path.isdir(os.path.join(directory, module_name)) and \
       os.path.exists(os.path.join(directory, module_name, '__init__.py')):
        return True
    return False

def get_external_modules():
    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    all_modules = set()
    for file in py_files:
        modules = extract_imports(file)
        all_modules.update(modules)
    # Filter out standard library and local modules
    external_modules = []
    for module in all_modules:
        if module.startswith('_'):
            continue
        if is_stdlib_module(module):
            continue
        if is_local_module(module):
            continue
        external_modules.append(module)
    return sorted(external_modules)

def get_version(module):
    try:
        result = subprocess.run(['pip', 'show', module], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':')[1].strip()
        return None
    except Exception:
        return None

if __name__ == '__main__':
    external_modules = get_external_modules()
    with open('requirements.txt', 'w') as f:
        for module in external_modules:
            version = get_version(module)
            if version:
                f.write(f'{module}=={version}\n')
            else:
                # If we can't get version, just write the module (let user handle version)
                f.write(f'{module}\n')