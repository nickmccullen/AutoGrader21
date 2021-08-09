import imp
import uuid
import time
import math
import numpy as np
import os
import sys
sys.path.append('.')

from Libs.Evaluation import Evaluation as Ev

import subprocess
from os import getpgid, killpg, setsid #, #kill, #getcwd
import signal

class Evaluation(Ev):
    """ This module is designed to mark the AR10366 course """
    
    # The plugin must have some kind of unique identifier assigned to it
    plugin_type = 'AR10336_EX_10'
    plugin_name = 'AR10336 - Exercise 10'
        
    def __init__(self):
        self.maxpoints=1
        self._feedback_string=''
        self._output_string=''
        self._error_string=''   
        
    def reset(self):
        self._feedback_string=''
        self._output_string=''
        self._error_string=''
    

    def mark(self, execution_string, *args):
        execution_timeout = 10 #s
        
        ##################################
        ###model code
        import numpy as np
        #import matplotlib.pyplot as plt

        def _fx(x):
            return np.exp(-x**2)

        #list for integral values
        _gvals=[]

        #constant offset (would need to obtain for particular problem).
        _g=0
        _dx=0.1

        _xvals=np.arange(-3,3,_dx)
        for x in _xvals:
            _g=_g+_fx(x)*_dx
            _gvals=_gvals+[_g]

        #plt.plot(xvals, gvals, "-o")

        ## save the figure file as a png image
        #plt.savefig('integral.png')
        #plt.show()
        ##################################
        
        rootpath = os.getcwd()        
        pypath = args[0]
        student_dir = args[1]
        
        print(f"Marking: {student_dir}; file={pypath}")
        
        if pypath=='':
            print("No .py file found")
            student_error = "No Python .py file found. Submit in the correct format."
            raise Exception("ExecutionError: No executable script found.")            
        
        os.chdir(student_dir)     
 
        self._points_received = self.maxpoints
        
        print(f"EXEC: {execution_string}")    
        #############################################################
        ### Run the student code and grab output as a first check ###
        student_output = ''
        student_error = ''
        try: 
            current_process = subprocess.run(execution_string, shell=True, bufsize=0, stdin=subprocess.PIPE, capture_output=True, close_fds=True, universal_newlines=True, preexec_fn=setsid, timeout=execution_timeout)
            student_output = str(current_process.stdout)
            student_error = str(current_process.stderr)
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
        ##############################################################
        
        ###################################################
        ### Run tests by importing the code as a module ###
        student_module = None
        imperr=False
        try: 
            fname = pypath
            
            contents = open(fname, "r").read()
            ftemp = fname.replace(".py", "_new.py")
                        
            with open(ftemp, "w") as newf:
                newconts = contents.replace("plt.", "#plt.").replace("import matplotlib", "#import matplotlib").replace("get_ipython()", "#get_ipython()")
                newf.write(newconts)
                
            student_module = imp.load_source(str(uuid.uuid4()), ftemp)
        except Exception as e: 
            self._feedback_string += ("\nThe code produced the error:\n"+str(e)+'\n')
            imperr=True
        
        try:
            assert student_module.gvals == _gvals
            #self._points_received = 2
            self._feedback_string += ("\nThe code produces the correct gvals.\n")
        except AssertionError:
            self._points_received -= 1
            self._feedback_string += ("\nYour gvals array contained the wrong values.\n")
        except ImportError:
            self._points_received -= 1
            self._feedback_string += ("\nThe gvals array could not be imported.\n")
        except AttributeError as e:
            self._points_received -= 1
            self._feedback_string += (str(e) + "\ndid you rename something you shouldn't have?")
        except Exception as e: 
            self._points_received -= 1
            os.chdir(rootpath) # in case something bad happens
            print("Exception raised: "+str(e))        
        finally:
            os.chdir(rootpath)
        ### end module tests ###############
        #####################################################
            
        self._clean_exit = True

        # Marking is done. No need to return anything
