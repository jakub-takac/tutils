#Here we have auxiliary functions containing most logic for tutils
import re
import os
from datetime import datetime
import inspect
import sys
from typing import Callable, List
from pathlib import Path

list_of_scripts=['separator', 'testscript', 'lister', 'uncommenter']

# This function takes as input a file (rather, its name, usually something like sys.argv[1]) as a string. It makes a copy of the file into the directory /path/to/tutil-log, where the path to file is /path/to/file. The backup copy has the name: name-of-file-date_time.extension-of-file. So that if file is example.txt, the copy is /path/to/tutil-log/example-date_time.txt. If this action is succesful, True is returned, if not, False is returned and an error message printed.
def log_backup(file):
    # This stores the path to the directory in which the file is located
    input_dir = os.path.dirname(os.path.abspath(file))
    # This stores the base name of the file, so that for example /path/to/example.txt file would yield example.txt
    name = os.path.basename(file)
    # This splits the file and the extension so that if name=example.txt then name_root=example and name_ext=.txt
    name_root, name_ext = os.path.splitext(name)

    #This stores the current time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print('Timestamp to be used for the backup file: ', timestamp)

    # This stores the directory for the log which will in this case look something like /path/to/tutil-log
    log_dir=os.path.join(input_dir, 'tutil-log')
    # This makes the directory tutil-log. If the directory already exists, it hopefully doesn't do anything
    os.makedirs(log_dir, exist_ok=True)

    # This stores the name of the backup file which will eventually be written in the log folder
    backup_name = f"{name_root}-{timestamp}{name_ext}"
    backup_path = os.path.join(log_dir, backup_name)

    # Checks if a backup file with the exact same name already exists and in this case does nothing. This should only happen if this function is called to the same file multiple times within the same second which should never happen.
    if os.path.exists(backup_path):
        print(f"Error: Backup file already exists: {backup_path}")
        print("This should only happen if this function has been called multiple times within the same second, which should NEVER happen")
        return False # This is so that whoever calles this function can verify if the backup has been made
    # First open file for reading as src (source), then open backup_path (full path to the backup file) for writing as dst (destination). Then reads from src and writes into dst.
    with open(file, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    # Print what has been done
    print(f'log_backup has been called for file {os.path.abspath(file)} and a backup copy has been saved as:\n', f'{backup_path}')
    return True # This is so that whoever calles this function can verify if the backup has been made

# This functions takes as argument a list of strings, where each entry is interpreted as a separate line. Then this is written into the file specifiad by its path 'out_path'
def print_file(file_l: list[str], out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
            for line in file_l:
                f.write(line + '\n')

class TArgParse:
    # default method for parsing optional arguments
    def defaultOptional(list_of_args: list[str]):
        list_optional_args=[]
        for arg in list_of_args:
            if arg.startswith('-'):
                list_optional_args.append(arg)
        return list_optional_args
    # default method for parsing positional arguments
    def defaultPositional(list_of_args: list[str]):
        list_positional_args = []
        for arg in list_of_args[1:]:
            if not arg.startswith('-'):
                list_positional_args.append(arg)
                if not arg[0].isalpha():
                    print("Warning: a strange argument has been passed. All positional arguments should start with a letter of the alphabet \n", "Continuing...")
        return list_positional_args
    
    def __init__(
            self,
            arg = sys.argv, 
            opt_method: Callable[[List[str]], List[str]] = defaultOptional, 
            man_method: Callable[[List[str]], List[str]] = defaultPositional, 
            custom=False
            ):
        self.user_argument = arg
        self.called = os.path.abspath(arg[0])
        caller = os.path.abspath(inspect.stack()[-1].filename)
        # This verifies that the parser has been called from the main script. I am not sure I like it but I really do not see why this should ever be called in a different way, as its intention is to literally parse the user input. Warning seems appropriate.
        self.caller_warning = not caller == self.called
        if not custom and self.caller_warning:
            print("Warning: Argument parser might have been called incorrectly. If you are a user there might be a problem with your input, try to type 'scriptname -h' for help. \n", "Continuing anyway.")
        # Initiate optional and positional arguments
        self.optional = opt_method(arg)
        self.positional = man_method(arg)
        # Initiate a help string
        self.help = f'To see detailed help, type {caller} --help'
        if not custom and self.caller_warning:
            self.help += f'\n You might also want to try {os.path.abspath(arg[0])} --help'
    
    # Functions for printing various values follow, mostly for debugging
    def print_arg(self):
        print(self.user_argument)
    def print_opt(self):
        print(self.optional)
    def print_pos(self):
        print(self.positional)

# Checks if a string encodes information about the locaiton of a valid text file with the correct encoding
def is_valid_text_file(filepath, encoding='utf-8', test_read_bytes=1024, strict = True):
    path = Path(filepath)
    # Recovers the extension of the file.
    extension = os.path.splitext(os.path.basename(path))[1] 
    valid_extensions=['.tex', '.txt']
    # Step 1: Check if the path exists and is a file
    if not path.is_file():
        return False
    
    # Step 2: Try opening it as a text file in the specified encoding
    try:
        with path.open('r', encoding=encoding) as f:
            # Step 3: Try reading a bit to confirm it's decodable
            f.read(test_read_bytes)
            if extension not in valid_extensions and strict:
                user_input = input("You have asked this script to adjust a file which does not have an extension of .txt or .tex.\n" +
                            "This script should only be applied to text files and is intended specifically for .tex files.\n" +
                            f"Are you sure you want the file {path} to be modified by this script? [y/N]")
                if user_input.strip().lower() == 'y':
                    return True
                else:
                    return False
        return True
    except (UnicodeDecodeError, OSError):
        # Catches binary files or encoding errors, or inaccessible files
        # I will not pretend I understand exception handling in Python. Been years since I last saw it and I will just trust ChatGPT for now.
        return False

# Lists available scripts
def lister():
    print('List of available scripts: \n')
    for scr in list_of_scripts:
        print(scr)

def scriptToRun(positional: list[str], called: str):
    if positional == []:
        print(f'You need to specify name of the script, e.g. "{called} separator". For list of scripts type "{called} lister".')
        sys.exit()
    if positional[0] not in list_of_scripts:
        msg = positional[0] + ' is not a valid name of a script that can be ran.\n' + f"Type '{called} lsscr' to see the list of available scripts or {called} --help for help"
        sys.exit(msg)
    else:
        return positional[0]
    
# def separator(file, force=False, verbose=True):
#     # Inform user of what will be modified
#     print("The file to be modified: " + file)
    
#     # Here we store the absolute path to the input file, so that if the user's working directory was ~/Documents/text-files and they passe example.txt, then this should resolve to /home/username/Documents/text-files/example.txt
#     path_to_input= os.path.abspath(file)
#     print("Absolute path to the file to be modified:" + path_to_input)

#     # This attempts to create a backup file in the tutil-log folder (subdirectory of the directory of the passed file). When it succeeds, it continues with the logic, otherwise prints a message and does nothing.
#     # FIX PERMISSIONS LATER []
#     if log_backup(file) or force:
#         # Here we store the modified file as a list of lines.
#         mf_l, number_of_adjustments = sentence_split(file, verbose)
#         # The modified file will overwrite the input file
#         print_file(mf_l, path_to_input)
#         print('Success!\n', f'The file: {path_to_input} has been modified and lines should be separated accordingly.')
#         print('The number of line splits carried out:', str(number_of_adjustments))
#     else:
#         print('Error: Cannot continue since a backup file cannot be created')

def uncommenter(path):
    counter = 0
    # Open the file and pass the lines to the variable 'lines'. The type is list. Each memeber of the list is a line.
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # Here we will store the modified list of lines where there should be exactly one sentence per line.
    modified_lines= []
    user_msg = f'\n Comments will be removed from {path} \n' + 'Do you wish to \n' '1) Remove comments and where a comment took up entire line leave a blank line (type "l" and enter) \n' + '2) Remove comments and where a comment took up entire line remove the line (type "r" and enter)\n' + '3) Abort (type "a" and enter)\n' + 'Typing anything else will result in option 1)'
    inp = input(user_msg).strip().lower()
    if inp == 'a':
        sys.exit()
    else:
        remove = inp == 'r'
    for line in lines:
        stripped_line = line.rstrip('\n')
        changed = False
        # Every line where % is the first character (even if there are some spacebars before) is removed. Lines which were empty from the beggining are preserved
        if not stripped_line.lstrip() == '':
            if stripped_line.lstrip()[0]== '%' and remove:
                counter += 1
                continue
        for i in list(range(len(stripped_line))):
            # Separate loogic on the first character as we cannot check the previous one for backslashes
            if i == 0:
                # If first character is %, we delete whole line (append an empty line)
                if stripped_line[i]=='%':
                    if not remove:
                        modified_lines.append('')
                    changed = True
                    counter += 1
                    break
                else:
                    continue
            # If the previous symbol was not backslash and current symbol is percent, then modify the line by leaving out the percent sign and everything after it
            if not stripped_line[i-1]== '\\' and stripped_line[i]=='%':
                modified_lines.append(stripped_line[:i])
                changed = True
                counter += 1
                break
            else:
                continue
        if not changed:
            modified_lines.append(stripped_line)
        else:
            continue
    return modified_lines, counter
    

# This function takes as argument a path to a text file and returns a separated list of sentences, which are modified so that lines with multiple sentences get split into separete lines. If the optional parameter count is True, then the function also returns the number of changes made as a second output.
def separator(path):
    counter = 0
    # Open the file and pass the lines to the variable 'lines'. The type is list. Each memeber of the list is a line.
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # Here we will store the modified list of lines where there should be exactly one sentence per line.
    modified_lines= []
    # This is the pattern for which we will be searching in each line of the original file, i.e. 'lines'.
    # Explanation of the argument:
        # r before the string signifies we use a raw string which treats backslashes as literal backslashes
        # ([.!?]) signifies ends of sentences
        # (\s+) is for the space after an end of a sentence
        # [A-Z] are the capital letters which likely follow in a new sentence (for now if a sentence happens to start with math mode or a number, this will just do nothing)
    pattern = re.compile(r'([.!?])(\s+)([A-Z])')

    # Loop which adjusts lines line by line
    for line in lines:
        # Preserve comments and empty lines.
        # Any line containing '%' is completely skipped.
        if '%' in line or line.strip() == '':
            modified_lines.append(line.rstrip())
            continue

        #pattern.sub looks for the pattern (which we compiled above) in the second argument (here line.rstrip()) and replaces it with the first argument, which here is a function
        # The function we pass takes as argument the match object and can inspect each of the matched patterns: m.group(1) (end of sentence) m.group(2) space, m.group(3) starting capital letter of next sentence.
        # The function returns what we want to happen to the pattern. I.e. a string which replaces the space with a new line \n.
        # This modified line is now stored in temp_line
        temp_line, n = pattern.subn(lambda m : f'{m.group(1)}\n{m.group(3)}', line.rstrip())
        counter+= n
        # Temp line is now added back to modified_lines. Since .split actually splits the temp_line (which is a string) into a list of strings, so .extend needs to be used    
        modified_lines.extend(temp_line.split('\n'))
    return modified_lines, counter


def runner(function, file, verbose=True, force=False, active = True):
    if not active:
        function()
        sys.exit()
    print(f"You called {function.__name__} to modify a file.")
     # Inform user of what will be modified
    print("The file to be modified: " + file)
    
    # Here we store the absolute path to the input file, so that if the user's working directory was ~/Documents/text-files and they passe example.txt, then this should resolve to /home/username/Documents/text-files/example.txt
    path_to_input= os.path.abspath(file)
    print("Absolute path to the file to be modified:" + path_to_input)

    # This attempts to create a backup file in the tutil-log folder (subdirectory of the directory of the passed file). When it succeeds, it continues with the logic, otherwise prints a message and does nothing.
    # FIX PERMISSIONS LATER []
    if log_backup(file) or force:
        # Here we store the modified file as a list of lines.
        mf_l, number_of_adjustments = function(file)
        # The modified file will overwrite the input file
        print_file(mf_l, path_to_input)
        print('Success!\n', f'The file: {path_to_input} has been modified by {function.__name__}.')
        print('The number of adjustments carried out:', str(number_of_adjustments))
    else:
        print('Error: Cannot continue since a backup file cannot be created')

                
