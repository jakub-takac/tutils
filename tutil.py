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
    help = '--help' in parsed.optional or '-h' in parsed.optional
    if help:
        print(t.help(sys.argv[0]))
        sys.exit()    
    # Go through all positional arguments
    print(force)
    script = t.scriptToRun(parsed.positional, parsed.called)
    if script == 'separator':
        for file in parsed.positional[1:]:
            t.runner(t.separator, file, verbose=verbose, force=force)
    
    if script == 'lister':
        t.runner(t.lister, '', active = False)

    if script == 'testscript':
        print('test')

    if script == 'uncommenter':
        for file in parsed.positional[1:]:
            t.runner(t.uncommenter, file, verbose=verbose, force=force)

#This makes it run only if the script is called directly by its name
if __name__ == "__main__":
    main()
else:
    print("Error: You called this script from within a different script. This script should only be called directly.")