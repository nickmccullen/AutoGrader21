import imp
import uuid
import time
import math
import sys
sys.path.append('.')

from Libs.Evaluation import Evaluation as Ev

import subprocess
import os, pandas as pd
from shutil import copyfile
from os import getpgid, killpg, setsid #, #kill, #getcwd
import signal


class Evaluation(Ev):
    """ This module is designed to mark the AR10366 course """

    # The plugin must have some kind of unique identifier assigned to it
    plugin_type = 'AR10366_EX_09'
    plugin_name = 'AR10366 - Exercise 9'  

    def __init__(self):
        self.maxpoints=3
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
        
        ##################
        ### model code ###
        import pandas as pd
        data = pd.read_excel("TaskFiles/soil_regression.xlsx").set_index("sample")
        x = data["PI (%)"]
        y = data["CBR (%)"]
        n=len(x)
        a0 = ( sum(x**2)*sum(y) - sum(x)*sum(x*y) )/( n*sum(x**2) - sum(x)**2 )
        a0=round(a0,6)
        a1 = ( n*sum(x*y) - sum(x)*sum(y) )/( n*sum(x**2) - sum(x)**2 )
        a1=round(a1,6)
        def prediction(a0, a1, x):
            y = a0 + a1*x 
            return y
        xnew = 30
        ypred = prediction(a0, a1, xnew)
        y_hat = prediction(a0, a1, x)
        residuals = y - y_hat
        devs_mean = y - y.mean()
        unexp_var = sum(residuals**2)
        total_var = sum(devs_mean**2)
        r2 = round(1 - unexp_var/total_var, 6)
        ### end model code ###
        ######################
        
        if args[0]=='':
            print("No .py file found")
            student_error = "No Python .py file found. Submit in the correct format."
            raise Exception("ExecutionError: No executable script found.")      
            
        rootpath = os.getcwd()        
        pypath = args[0]            
        
        student_dir = args[1]
        os.chdir(student_dir)
                
        self._points_received = 0 #self.maxpoints

        try:
            os.mkdir("Files")
        except: pass    
        copyfile(f"{rootpath}/TaskFiles/soil_regression.xlsx", "Files/soil_regression.xlsx")
        copyfile(f"{rootpath}/TaskFiles/soil_regression.xlsx", "soil_regression.xlsx")
          
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

            #self._feedback_string += (
            #    'The output of your script was: \n'
            #       + '\n[ Start of output ]\n'
            #       + student_output
            #       + '\n[ End of output ]\n')
            ### END OF RUNNING STUDENT CODE ###
            ###################################
            
            ###################################
            ### run tests on student module ###
            student_module = None
            
            stufile = args[0]
            
            newfile = "runme.py"
            with open(newfile, "w") as sfile:
                sfile.write(open(stufile, "r").read().replace("print", "#print"))
            
            student_module = imp.load_source(str(uuid.uuid4()), newfile)
            
            ### test 1
            self._feedback_string+="\nPart 1:\n"
            try: 
                c,m = round(student_module.a0,6), round(student_module.a1,6)
                assert (c, m)==(a0,a1)
                self._points_received +=1
                self._feedback_string+="PASSED!\n\n"
            except AssertionError:
                self._feedback_string+="Your code produced different values of a0 and a1 to those expected.\n"
                self._feedback_string+=f"Expected: a0={a0}, a1={a1}; got: a0={c}, a1={m}\n"
                #self._feedback_string+="Your code produced a different fit when used on different test data.\nDid you hard-code any values rather than obtaining them from the data itself?\n"
            except exception as e:
                self._feedback_string+=str(e)
            
            ### test 2
            self._feedback_string+="\nPart 2:\n"
            b0=5; b1=-0.1; x=20
            y0 = round(prediction(b0, b1, 20),6) # should be 3.0
            try: 
                y1 = student_module.prediction(b0, b1, 20)
                assert y0==y1
                self._points_received +=1
                self._feedback_string+="PASSED!\n\n"
            except AssertionError:
                self._feedback_string+="Your linear fit function produced a different fit when used with different parameter values (a0=5, a1=-0.1).\nDid you hard-code some values rather than using the arguments to the function?\n"
                self._feedback_string+=f"Expected: y(x=20)={y0}; got: y(x=20)={y1}\n"
            except exception as e:
                self._feedback_string+=str(e)
                
            
            ### test 3
            self._feedback_string+="\nPart 3:\n"
            try:
                x = round(student_module.r2,6)
                assert x==r2
                self._points_received +=1
                self._feedback_string+="PASSED!\n\n"
            except AssertionError:
                self._feedback_string+="Your code produced a different R^2 value to that expected.\n"
                self._feedback_string+=f"Expected: r2={r2}; got: r2={x}\n"
                #self._feedback_string+="Your code produced a different r2 value for a fit on different test data.\nDid you hard-code any values rather than obtaining them from the data itself?\n"
            except exception as e:
                self._feedback_string+=str(e)
                
            ### end tests on student module ###
            ###################################

                    
        except Exception as e: 
            os.chdir(rootpath) # in case something bad happens
            print("Exception raised: "+str(e))
        finally: os.chdir(rootpath) # in case something bad happens

        # Mark that the program completed alright
        self._clean_exit = True
        
        


        # Marking is done. No need to return anything
        #finally:
        #time.sleep(1)
        #subprocess.run("killall python3.8", shell=True, bufsize=0, stdin=subprocess.PIPE)