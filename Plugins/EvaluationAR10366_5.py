import imp
import uuid
import time
import math
import sys
sys.path.append('.')

from Libs.Evaluation import Evaluation as Ev

import subprocess 
from os import getpgid, killpg, setsid #, #kill, #getcwd
import signal


class Evaluation(Ev):
    """ This module is designed to mark the AR10366 course """

    # The plugin must have some kind of unique identifier assigned to it
    plugin_type = 'AR10366_EX_05'
    plugin_name = 'AR10366 - Exercise 5'  

    def __init__(self):
        #super().__init__()
        self.maxpoints=2
        self._feedback_string=''
        self._output_string=''
        self._error_string=''
    

    def funtime(target, args=(), timeout=1):
        """Function to exectute a function with a timeout"""
        def handler(signum, frame):
            raise Exception("TimeOut")
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)
        try:
            result = target(*args)
            signal.alarm(0) #resets the clock
            return result
        except Exception as e: 
            raise e      
        
     
    def reset(self):
        self._feedback_string=''
        self._output_string=''
        self._error_string=''    

    #def mark(self, sandbox, *args):
    def mark(self, execution_string, *args):
        funtime = Evaluation.funtime
        
        ##################
        ### model code ###
        def MODEL_quadmap(c): 
            xvals=[]
            x = 0.5
            for i in range(10000):
                x = c - x**2
            for i in range(16):
                x = c - x**2
                xvals.append(x)
            return xvals        
        ### end model code ###
        ######################
        
        # We set a short timeout to avoid programs running away forever
        #sandbox.setExecutionTimeout(.5)
        execution_timeout = 1 #s
        
        if args[0]=='':
            print("No .py file found")
            student_error = "No Python .py file found. Submit in the correct format."
            raise Exception("ExecutionError: No executable script found.")
        
        #else:        # may not be neded with above raise
        
        self._points_received = 0

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


        
        # Give the students points that are removed if they were wrong
        self._points_received = 0

        # We start tracking a reference to the module outside the try, so that it can be deleted after
        student_module = None

        ########################
        ### TESTS BEGIN HERE ###
        try:
            # It is important to load modules with unique names, since they stick in the namespace
            student_module = imp.load_source(str(uuid.uuid4()), args[0].strip('\''))
            
            # run tests
            # Test 1:
            try:
                quadmap = student_module.quadmap              
                q1 = quadmap(1.3)
                p1 = MODEL_quadmap(1.3)
                assert q1==p1
                self._points_received +=1
            except TypeError: self._feedback_string +='Your quadmap function does not take the correct arguments.'
            except AssertionError: 
                self._feedback_string +=f'''The wrong values were returned.\n'''
                if type(q1)!=type(p1):
                    self._feedback_string +="Your function does not return a list!\n"
                elif len(q1)!=len(p1):
                    self._feedback_string +=f"Your list has {len(q1)} elements not the expected {len(p1)}.\n"
                else:
                    self._feedback_string +=f'''Check the following:
                * Are you iterating for 10000 (ten thousand) iterations **before** saving any values to your list?
                * The return statement should be outside the for loop or it will exit the loop after only one iteration.

                The output of your function was:
                {q1}

                it should have been:
                {p1}'''
                    
            # Test 2:
            try:
                quadmap = student_module.quadmap
                c = 1.1
                q1 = quadmap(c)
                p1 = MODEL_quadmap(c)
                assert q1==p1
                self._points_received +=1
            except TypeError as e: self._feedback_string +='the argument c may be being used incorrectly: '+str(e)
            except AssertionError: 
                self._feedback_string +=f'''The wrong values were returned with c=1.1\n Check the function argument c is being used in the calculations.'''
                if type(q1)!=type(p1):
                    self._feedback_string +="Your function does not return a list!\n"
                elif len(q1)!=len(p1):
                    self._feedback_string +=f"Your list has {len(q1)} elements not the expected {len(p1)}.\n"
                else:
                    self._feedback_string +=f'''Check the following:
                * Are you iterating for 10000 (ten thousand) iterations **before** saving any values to your list?

                The output of your function was:
                {q1}

                it should have been:
                {p1}'''                    

                #self._points_received = 1
            except NameError as e: 
                print(str(e))
                #self._points_received = 1
            except AttributeError as e: 
                print(str(e))
                self._error_string += 'NameError: '+str(e)#No function named "quadmap" found in your submitted module'
                #self.points_received -= 1
            except Exception as e: 
                print(str(e))
                self._error_string +="Your function causes an unexpected error: "+str(e)
                #self.points_received -= 1
                
        except Exception as e:
            # Mark that the something didn't go alright
            self._error_string += "Submitted file could not be loaded as a module."
            self._error_string += '\n\r' + str(e)
            self._points_received = 0
            self._clean_exit = False

        ### END OF TESTS ###
        ####################
        finally:
            try:
                del student_module
            except:
                pass
        # Mark that the program completed alright
        self._clean_exit = True


        # Marking is done. No need to return anything
        #finally:
        #time.sleep(1)
        #subprocess.run("killall python3.8", shell=True, bufsize=0, stdin=subprocess.PIPE)