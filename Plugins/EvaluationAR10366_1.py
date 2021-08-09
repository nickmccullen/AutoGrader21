import re

from Libs.Evaluation import Evaluation as Ev

import subprocess 
from os import getpgid, killpg, setsid #, #kill, #getcwd
import signal


class Evaluation(Ev):
    """ This module is designed to mark the AR10366 course """

    # The plugin must have some kind of unique identifier assigned to it
    plugin_type = 'AR10336_EX_01'
    plugin_name = 'AR10336 - Exercise 1'
    
    def __init__(self):
        #super().__init__()
        self.maxpoints=2
        self._feedback_string=''
        self._output_string=''
        self._error_string=''
        
    def reset(self):
        self._feedback_string=''
        self._output_string=''
        self._error_string=''

    def mark(self, execution_string, *args):
        # We set a short timeout to avoid programs running away forever
        execution_timeout = 1 #s
        
        # submitted python script should be first argument: args[0]
        pypath = args[0]
        if pypath=='':
            print("No .py file found")
            student_error = "No Python .py file found. Submit in the correct format."
            raise Exception("ExecutionError: No executable script found.")
        
        
        self._points_received = 2
        #############################################################
        ### Run the student code and grab output as a first check ###        
        student_output = ''
        student_error = ''          

        # Run the test first test
        try:
            current_process = subprocess.run(execution_string, shell=True, bufsize=0, stdin=subprocess.PIPE, capture_output=True, close_fds=True, universal_newlines=True, preexec_fn=setsid, timeout=execution_timeout)
            
            student_output = str(current_process.stdout)
            student_error = str(current_process.stderr)
        except subprocess.TimeoutExpired as e: 
            print(str(e))
            self._feedback_string += "Your code took too long and timed out. Make sure that loops can terminate and nothing is growing exponentially. Go through the notes and examples carefully and use the format given in the task."
            self._points_received -=1
            self._clean_exit = False 
            raise
        except Exception as e:
            # Mark that the something didn't go alright
            self._error_string = ("There was an error running the student's work: "
             + '\n\r' + str(e))
            self._points_received -=1
            self._clean_exit = False     
            raise
        #except: raise Exception("Could not run student script.")
        finally: 
            try: killpg(getpgid(current_process.pid), signal.SIGKILL) # should work 
            except: subprocess.run("killall python3.8", shell=True, bufsize=0, stdin=subprocess.PIPE) # clean up anyway 
                
        self._output_string = student_output

        self._feedback_string += (
            'The output of your script was: \n'
               + '\n[ Start of output ]\n'
               + student_output
               + '\n[ End of output ]\n')
        ### END OF RUNNING STUDENT CODE ###
        ###################################


        # Add the student output to output
        self._output_string = student_output

        # Add the student output to the feedback
        self._feedback_string = (
            'The output of your script was: \n'
              + '\n[ Start of output ]\n'
              + student_output
              + '\n[ End of output ]\n')

        # Record any error the student's code might have thrown
        self._error_string = student_error


        # Check if the student missed any outputs
        for answer in ['Hello World!', '42']:
            if answer.lower() not in student_output.lower():
                self._points_received -=1

                # Give feedback
                self._feedback_string = (
                      "\nCommon mistakes: "
                    + "\n\t1. Don't forget 'print()' functions around all things you want to print for it to produce outputs."
                    + "\n\t2. Watch the spelling of strings, and don't change what you were asked to print in any way (a client wouldn't like that!)"
                    + "\n\tThe output should have been:"
                    + "\n\t\tHello World!"
                    + "\n\t\t42"
                    + "\n\n\twhere the 42 is an integer!")


        # Check if the student used any bad code (we passed the student's file path in the arguments)
        student_code = open(pypath, "r").read()

        # Look for bad print patterns
        if bool(re.search('^[^\#]*print(42)', student_code, re.MULTILINE)):
            self._points_received -=1

            # Give feedback
            self._feedback_string += ("\nIncorrect code detected! You were asked to calculate the answer and not just print the result."
                + "\nTry Again!"
                + "\nYour code is copied below:\n"
                + "\n[ Start of code ]\n"
                + student_code
                + "\n[ End of code ]\n")

        # Mark that the program completed alright
        self._clean_exit = True




