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

def get_external_modules():
    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    all_modules = set()
    for file in py_files:
        modules = extract_imports(file)
        all_modules.update(modules)
    # Remove standard library modules
    std_lib = set(sys.builtin_module_names)
    # Also add common standard library modules that might not be in builtin_module_names
    common_stdlib = {'os', 'sys', 're', 'json', 'csv', 'math', 'collections', 'itertools', 'functools',
                     'heapq', 'bisect', 'array', 'weakref', 'types', 'copy', 'pprint', 'reprlib',
                     'enum', 'numbers', 'decimal', 'fractions', 'random', 'secrets', 'statistics',
                     'datetime', 'itertools', 'collections', 'array', 'weakref', 'types', 'copy',
                     'pprint', 'reprlib', 'enum', 'numbers', 'cmath', 'decimal', 'fractions', 'random',
                     'secrets', 'statistics', 'itertools', 'collections', 'array', 'weakref', 'types',
                     'copy', 'pprint', 'reprlib', 'enum', 'numbers', 'cmath', 'decimal', 'fractions',
                     'random', 'secrets', 'statistics', 'itertools', 'collections', 'array', 'weakref',
                     'types', 'copy', 'pprint', 'reprlib', 'enum', 'numbers', 'cmath', 'decimal',
                     'fractions', 'random', 'secrets', 'statistics', 'itertools', 'collections', 'array',
                     'weakref', 'types', 'copy', 'pprint', 'reprlib', 'enum', 'numbers', 'cmath', 'decimal',
                     'fractions', 'random', 'secrets', 'statistics'}
    std_lib.update(common_stdlib)
    external_modules = [m for m in all_modules if m not in std_lib and not m.startswith('_')]
    return sorted(external_modules)

if __name__ == '__main__':
    external_modules = get_external_modules()
    for module in external_modules:
        try:
            # Use pip show to get the version
            result = subprocess.run(['pip', 'show', module], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Extract version from the output
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':')[1].strip()
                        print(f'{module}=={version}')
                        break
                else:
                    # If version not found, just print the module
                    print(module)
            else:
                # If pip show fails, just print the module (maybe not installed via pip)
                print(module)
        except Exception as e:
            print(f'{module}  # Error: {e}')