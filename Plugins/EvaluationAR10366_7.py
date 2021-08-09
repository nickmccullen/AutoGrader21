import imp
import uuid
import time
import math
import sys
sys.path.append('.')

from Libs.Evaluation import Evaluation as Ev

import subprocess
import os, numpy as np
from shutil import copyfile
from os import getpgid, killpg, setsid #, #kill, #getcwd
import signal


class Evaluation(Ev):
    """ This module is designed to mark the AR10366 course """

    # The plugin must have some kind of unique identifier assigned to it
    plugin_type = 'AR10366_EX_07'
    plugin_name = 'AR10366 - Exercise 7'  

    def __init__(self):
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
        execution_timeout = 10 #s
        
        if args[0]=='':
            print("No .py file found")
            student_error = "No Python .py file found. Submit in the correct format."
            raise Exception("ExecutionError: No executable script found.")
        
                
        self._points_received = self.maxpoints
        MODELoutput=np.loadtxt("TaskFiles/MODELTASK6-energy_totals.txt")

        rootpath = os.getcwd()        
        pypath = args[0]

        student_dir = args[1]
        os.chdir(student_dir)
        print(f"CWD: {os.getcwd()}")         
        student_files = os.listdir('.')
        print(f"LS: {student_files}")                                        
        [os.remove(f) for f in student_files if f[-4:].lower()=='.txt']
        student_files = os.listdir('.')
        print(f"LS: {student_files}")
        try:
            os.mkdir("Files")
        except: pass    
        copyfile(f"{rootpath}/TaskFiles/houseenergy.csv", "Files/houseenergy.csv")
        
          
        # reset execution string for this task as running in a different location
        #execution_string = f"python3.8 {rootpath}/{pypath}"
        print(f"EXEC: {execution_string}")                                      
        try:
            #############################################################
            ### Run the student code and grab output as a first check ###
            student_output = ''
            student_error = ''                 
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
            # for any figures generated
            student_files = os.listdir('.')
            print(student_files)
            textfiles = [f for f in student_files if f[-4:].lower()=='.txt']
            print(f"{textfiles}")
            print(len(textfiles))
            if len(textfiles)==0:
                self._feedback_string += "Your python script did not generate any file with a .txt extension.\n\n"
                self._points_received -=1
            elif len(textfiles)==1:
                print("here")
                outputfile = textfiles[0]
                try: Soutput=np.loadtxt(outputfile)
                except Exception as e: 
                    Soutput=None
                if str(MODELoutput)!=str(Soutput):
                    print("this")
                    self._feedback_string += "Your output file contains the wrong data!."
                    self._points_received -=1
                else: self._points_received=self.maxpoints
            else: 
                self._feedback_string += "Your script produces more than one text file so cannot be checked automatically."
                self._points_received -=1
                    
        except: os.chdir(rootpath) # in case something bad happens
        finally: os.chdir(rootpath) # in case something bad happens

        # Mark that the program completed alright
        self._clean_exit = True
        
        


        # Marking is done. No need to return anything
        #finally:
        #time.sleep(1)
        #subprocess.run("killall python3.8", shell=True, bufsize=0, stdin=subprocess.PIPE)