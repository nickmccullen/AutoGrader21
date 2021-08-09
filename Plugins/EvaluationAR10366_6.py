import imp
import uuid
import time
import math
import sys
sys.path.append('.')

from Libs.Evaluation import Evaluation as Ev

import subprocess
import os
from os import getpgid, killpg, setsid #, #kill, #getcwd
import signal


class Evaluation(Ev):
    """ This module is designed to mark the AR10366 course """

    # The plugin must have some kind of unique identifier assigned to it
    plugin_type = 'AR10366_EX_06'
    plugin_name = 'AR10366 - Exercise 6'  

    def __init__(self):
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

    def mark(self, execution_string, *args):
        funtime = Evaluation.funtime
        
        # We set a short timeout to avoid programs running away forever
        execution_timeout = 10 #s
        
        if args[0]=='':
            print("No .py file found")
            student_error = "No Python .py file found. Submit in the correct format."
            raise Exception("ExecutionError: No executable script found.")
        
                
        self._points_received = 1
        
        rootpath = os.getcwd()
        figpath = f"{rootpath}/Ex06Figs/"
        try: os.mkdir(figpath)
        except: pass
        
        pypath = args[0]
        student_ID = pypath.strip('.py').replace("Extracted-Task-6", "").replace('/', '')
        with open(f"{figpath}/index.html", "a") as html:
            html.write(f'<hr><br><h1>{student_ID}</h1><br>')

        student_dir = args[1]
        os.chdir(student_dir)
        student_files = os.listdir('.')
        pngs = [f for f in student_files if f[-3:].lower()=='png']
        print(pngs)
        if len(pngs)>0:
            self._points_received += 1
        else:
            self._feedback_string += "No file with a .png extension found in the submission.\n\n"
        
        with open(f"{figpath}/index.html", "a") as html:    
            html.write(f'<h2>Submitted files:</h2><br>')
            for n in pngs:
                figname = f"{student_ID}_sub_{n}"
                os.rename(n, f"{figpath}/{figname}")
                html.write(f'<br><img src="s{figname}"><br>')
            
        # reset execution string for this task as running in a different location
        execution_string = f"python3.8 {rootpath}/{pypath}"
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
            pngs = [f for f in student_files if f[-3:].lower()=='png']
            print(pngs)
            if len(pngs)==0:
                self._feedback_string += "Your python script did not generate any file with a .png extension.\n\n"
                self._points_received -=1
            with open(f"{figpath}/index.html", "a") as html:    
                html.write(f'<h2>Generated files:</h2><br>')
                for n in pngs:
                    figname = f"{student_ID}_gen_{n}"
                    os.rename(n, f"{figpath}/{figname}")
                    html.write(f'<br><img src="{figname}"><br>')
                html.write(f'<hr><br>')
        except: os.chdir(rootpath) # in case something bad happens
        finally: os.chdir(rootpath) # in case something bad happens
            

        

        # We start tracking a reference to the module outside the try, so that it can be deleted after
        student_module = None

        ########################
        ### TESTS BEGIN HERE ###
        testfaults = False
        import numpy as np
        import matplotlib
        xdata = np.arange(300)
        ydata = np.random.normal(50, 15, 300) 
        try:
            # It is important to load modules with unique names, since they stick in the namespace
            student_module = imp.load_source(str(uuid.uuid4()), args[0].strip('\''))
                       
            # run tests
            # Test 1:
            try:
                plotter = student_module.plotter              

                fig = plotter(xdata, ydata)

                try: figprops = fig.properties()
                except AttributeError as e: 
                    self._feedback_string += ("It doesn't look like you generated a figure (fig) object properly using .subplots()")
                    testfaults = True
                    self._points_received -=1
                except Exception as e: 
                    self._error_string += str(e)
                    testfaults = True
                    self._points_received -=1
                try: 
                    aXs = fig.axes

                    if len(aXs)==1: 
                        self._feedback_string += ("Your Figure only has one set of axes")
                    if len(aXs)!=2: 
                        self._feedback_string += ("Your Figure should have exactly two sets of axes")
                        testfaults = True
                    (nr,nc,n) = aXs[0].get_geometry()
                    if (nr,nc)!=(1,2): 
                        self._feedback_string += (f'''Your figure canvas has {nr} rows and {nc} columns,
                    but it should be a 1x2 grid of axes, specify the correct nrows and ncols in plt.subplots()\n''') 
                        testfaults = True
                    else:
                        props0 = aXs[0].properties()
                        props1 = aXs[1].properties()                 
                        lines1 = [p for p in props0["children"] if type(p)==matplotlib.lines.Line2D]
                        if len(lines1)==0:
                            self._feedback_string += ("The first (left) axes contain no plotted lines\n")
                            self._points_received -=1
                            testfaults = True
                        else:    
                            prop1 = lines1[0].properties()

                            if prop1["xdata"].all() != xdata.all():
                                self._feedback_string += ("You have not plotted the correct x-values in the left plot.\n")
                                testfaults = True
                            if prop1["ydata"].all() != ydata.all():
                                self._feedback_string += ("You have not plotted the correct y-values in the left plot.\n")
                                testfaults = True
                            if aXs[0].get_xlabel()=='': 
                                self._feedback_string += ("You have no xlabel on the first Axes\n")
                                testfaults = True
                            if aXs[0].get_ylabel()=='': 
                                self._feedback_string += ("You have no ylabel on the first Axes\n")
                                testfaults = True
                            if aXs[0].get_title() =='': 
                                self._feedback_string += ("You have no title on the first Axes\n")
                                testfaults = True

                        rect2 = [p for p in props1["children"] if type(p)==matplotlib.patches.Rectangle]

                        if len(rect2)==1: 
                            self._feedback_string += ("There are no histogram boxes plotted on right second (right hand) axes\n")
                            testfaults = True
                            self._points_received -=1
                        else: 
                            if aXs[1].get_xlabel()=='': 
                                self._feedback_string += ("You have no xlabel on the second Axes\n")  
                                testfaults = True
                            if aXs[1].get_title() =='': 
                                self._feedback_string += ("You have no title on the second Axes\n")
                                testfaults = True

                except AttributeError as e: 
                    self._feedback_string += ("You needed to generate separate axes using fig, ax = ... or fig, (ax1, ax2) = ...")
                    self._points_received -=1
                    testfaults = True

            except NameError as e: 
                print(e)
                if str(e)=="name 'plt' is not defined":
                    self._error_string +=("NameError: "+str(e))
                    self._feedback_string += ("\nplt not found. Did you import the matplotlib.pyplot library correctly?")
                    testfaults = True
                if str(e)=="name 'fig' is not defined":
                    self._error_string +=("NameError: "+str(e))
                    self._feedback_string += ("\nIt doesn't look like you generated a figure (fig) object properly using .subplots()")
                    testfaults = True
                    self._points_received -=1
            except AttributeError as e: 
                print(str(e))
                self._error_string += 'NameError: '+str(e)#No function named "quadmap" found in your submitted module'
                #self.points_received -= 1
            except Exception as e: 
                print(str(e))
                self._error_string +="Your function causes an unexpected error: "+str(e)
                #self.points_received -= 1
            if not testfaults: self._points_received += 1    
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