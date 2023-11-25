import os
import subprocess
import fnmatch

# This Python Programm Converts a Jupyter Notebook to a Python Script and vice versa if the modification time of the file is newer than the other file


# Check if Jupytext is installed; if not, install it
try:
    import jupytext
except ImportError:
    subprocess.run(['python', '-m', 'pip', 'install', 'jupytext'])

script_filename = os.path.basename(__file__)

# Get a list of all files in the current directory
current_dir = os.getcwd()
file_list = os.listdir(current_dir)
# remove own file
file_list = [filename for filename in file_list if filename != script_filename]


def is_valid_py_file(py_file):
    with open(py_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if '#%%' in line or '# %%' in line:
                return True
        return False

# Function to check if a file exists
def file_exists(file_path):
    return os.path.isfile(file_path)

# Function to convert .ipynb to .py:percent
def convert_ipynb_to_py_percent(ipynb_file):
    subprocess.run(['python', '-m', 'jupytext', '--to', 'py:percent', ipynb_file])

# Function to convert .py:percent to .ipynb
def convert_py_percent_to_ipynb(py_percent_file):
    subprocess.run(['python', '-m', 'jupytext', '--to', 'notebook', py_percent_file])

# Define a list of file extensions to consider
valid_extensions = {'.py', '.ipynb'}

# Iterate through all files in the directory
for filename in file_list:
    name, extension = os.path.splitext(filename)
    
    # Check if the file has a valid extension and is not in the .git folder
    if extension in valid_extensions and not fnmatch.fnmatch(filename, '.git*'):
        ipynb_file = name + '.ipynb'
        py_percent_file = name + '.py'


        if file_exists(ipynb_file) and file_exists(py_percent_file):
            ipynb_mtime = os.path.getmtime(ipynb_file)
            py_percent_mtime = os.path.getmtime(py_percent_file)

            if ipynb_mtime > py_percent_mtime:
                # .ipynb is newer, delete .py:percent and convert .ipynb to .py:percent
                os.remove(py_percent_file)
                convert_ipynb_to_py_percent(ipynb_file)
            elif ipynb_mtime < py_percent_mtime and is_valid_py_file(py_percent_file):
                # .py:percent is newer, delete .ipynb and convert .py:percent to .ipynb
                os.remove(ipynb_file)
                convert_py_percent_to_ipynb(py_percent_file)
            elif ipynb_mtime == py_percent_mtime:
                print(f'Both {ipynb_file} and {py_percent_file} have the same modification time')
        else:
            if file_exists(ipynb_file):
                # Only .ipynb exists, convert it to .py:percent
                convert_ipynb_to_py_percent(ipynb_file)
                print(f'Converted {ipynb_file} to ipython script')
            elif file_exists(py_percent_file) and is_valid_py_file(py_percent_file):
                # Only .py:percent exists, convert it to .ipynb
                convert_py_percent_to_ipynb(py_percent_file)
                print(f'Converted ipython script {py_percent_file} to notebook')

if __name__ == '__main__':
    pass