#!/usr/bin/python3

#This script will take as input a string and output the number of times each letter appears.

#General modules
import sys
import os
import argparse

#Tutil modules
import tutilfs as t



def main():
    # Parse user input
    parsed = t.TArgParse()
    #Verbosity doesn't really work yet
    verbose = not '-nv' in parsed.optional
    force = '-f' in parsed.optional
    
    # Go through all positional arguments
    script = t.scriptToRun(parsed.positional, parsed.called)
    if script == 'separator':
        for file in parsed.positional[1:]:
            if not t.is_valid_text_file(file):
                print(f"{file} is not a valid argument. Only existing text files in utf8 encoding are valid")
                continue
            t.runner(t.separator, file, force, verbose)
    
    if script == 'lister':
        t.runner(t.lister, '', active =False)

    if script == 'testscript':
        print('test')

    if script == 'uncommenter':
        for file in parsed.positional[1:]:
            if not t.is_valid_text_file(file):
                print(f"{file} is not a valid argument. Only existing text files in utf8 encoding are valid")
                continue
            t.runner(t.uncommenter, file, force, verbose)

#This makes it run only if the script is called directly by its name
if __name__ == "__main__":
    main()
else:
    print("Error: You called this script from within a different script. This script should only be called directly.")