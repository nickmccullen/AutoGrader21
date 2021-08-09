import sys, os
sys.path.append('.')

from os import listdir, mkdir, getcwd
#from Libs.SandboxInsecure import SandboxInsecure
import  imp
from shutil import copyfile


class TestAR10366_Bulk:   
    
    def __init__(self):
        self.plugin_number=None
        self.gradebook_name=None
        self.submission_name=None
        self.maxpoints = 2
        self.extract = False
        self.pretest = False
        self.debugnumber=0 #set to zero to run all student files

    def run(self): 
        self._feedback_string=''
        self._points_received=self.maxpoints
    
        gradebook_name=self.gradebook_name
        plugin_number=self.plugin_number
        submission_name=self.submission_name
        self.plugin_path = f'Plugins/EvaluationAR10366_{plugin_number}.py'    
        self.module_name = f'AR10366_EX_{plugin_number}'
        infile = gradebook_name
        gradefile = f"New_Grades-Task-{plugin_number}.csv"
        with open(gradefile, 'w') as gfile:
            gfile.write(open(infile, 'r').readlines()[0]) 
            
        feedback_dir = f"Feedback-Task-{plugin_number}"
        try: mkdir(feedback_dir)
        except: pass

        rootpath = os.getcwd() 
        edir = f"{rootpath}/Extracted-Task-{plugin_number}/"
        if self.extract: 
            try: mkdir(edir)
            except: pass
            contents = listdir(submission_name)
            try: contents.remove("__pycache__")
            except: pass  
            for student_dir in sorted(listdir(submission_name)):
                submitted_files = listdir(submission_name+'/'+student_dir)
                for src in submitted_files:
                    student_dir2=student_dir.replace(' ','__')
                    source = submission_name+'/'+student_dir+'/'+src
                    dest = edir+student_dir2+src.replace(" ","__").replace("(", "").replace(")", "")
                    try: copyfile(source, dest)
                    except Exception as e: print(e)
                    
        df={}
        # Loop through the folders of students:
        dirlist = sorted(listdir(submission_name))
        try: dirlist.remove("__pycache__")
        except: pass
        try: dirlist.remove(".ipynb_checkpoints")
        except: pass
        if self.debugnumber>0: dirlist = dirlist[0:self.debugnumber]
        for student_dir in dirlist:
            # list contents of submission directory
            print(submission_name+'/'+student_dir)
            subfiles = os.listdir(submission_name+'/'+student_dir)
            # initialise submission file to blank
            student_file = ''
            filetype=None
            # loop through and identify the .py submission
            pycount = 0
            for f in subfiles:
                ft = f.split('.')[-1]
                if ft.lower()=='py':
                    student_file = f
                    pycount+=1
                if ft.lower() in ['ipynb', 'png', 'jpg', 'jpeg'] and self.plugin_number!=6:
                    filetype=f'.{ft}'
                         
            subpath = rootpath+'/'+submission_name+'/'+student_dir #+'/'+student_file
            pp = edir+student_dir+student_file
            pypath = pp.strip("'").replace(" ","__").replace("(", "").replace(")", "") 
            
            FB=''
            if pycount>1: FB+='You  submitted more than one .py file so only one of them was checked'
            if student_file=='':
                FB+='No Python *.py file was uploaded in the moodle submission area. '
                pypath = None
            if filetype!=None:
                FB+=f'You submitted a {filetype} file, which cannot be marked. Please submit only the file types asked for. '
            
            ID=' '.join(student_dir.split('_')[0:2]) #'"Participant
            
            points = 0
            if pypath!=None:
                # run the copied file in the original submission directory
                points = self.run_file(pypath, subpath)

                if int(float(points))==self.maxpoints: 
                    FB += "Your file runs correctly, Well done! (Also see feedback file on moodle)."
                elif self.pretest: 
                    FB += "Please see attached feedback text file and resubmit. "
                else: 
                    FB += "See feedback file uploaded on moodle. "
                #Next time submit before Wednesday morning to get early feedback and a chance to resubmit."'

                if " " in student_file: 
                    FB += "Your filename contains spaces! Please don't do this again."
                    
            elif self.pretest: 
                FB += "This time you will be allowed one more chance to resubmit correctly by Wednesday. "
                
            print("+++\nInline Feedback: "+FB+"\n---")
            
            df[ID]=str(points),FB
            try:
                with open("backup.csv", "a") as bkp:
                    bkp.write(",".join([ID,str(points),FB])+'/n')
            except: 
                with open("backup.csv", "w") as bkp:
                    bkp.write(",".join([ID,str(points),FB])+'/n')

        return df 


    def run_file(self, pypath, submission_path):

        module_name=self.module_name
        plugin_path=self.plugin_path
        
        target_module = imp.load_source(module_name, plugin_path)
        #plugin = getattr(target_module, 'Evaluation')
        plugin = target_module.Evaluation
              
        # Prep the command line instruction
        execution_string = 'python3.8 ' + pypath

        # The arguments to pass to the marking function.
        # The first argument should ALWAYS be the path to the student's file
        args = [pypath, submission_path]

        # Clear out fields that might be left from a previous run
        plugin.reset(self)

        # Run the plugin
        plugin.mark(self, execution_string, *args)

        Spoints = str(plugin.getPointsReceived(self))
        Scleanexit = str(plugin.getCleanExit(self))
        Soutput = str(plugin.getOutput(self))
        Serror = str(plugin.getError(self))
        Sfeedback = str(plugin.getFeedback(self))  
        #print("++++++++++++++++++++++++"+Sfeedback+"============================")
         
        if int(Spoints) < self.maxpoints:
            try: 
                student_code = open(pypath, 'r').read()
                Sfeedback += (
                          '\nSubmitted code below:\n'
                          + '\n[ Start of code ]\n'
                          + student_code
                          + '\n[ End of code ]\n')   
            except: Sfeedback += ("\nYou did not submit a file that can be opened in a Python text editor (such as Spyder)!\n")
        
        fbfile = pypath.replace('Extracted', 'Feedback').replace('__', ' ').replace('.py', '')+'_feedback.txt'
        with open(fbfile, 'w') as fbfile:
            fbfile.write(( 
                '\r\nPoints received: {0}\n' +
                #'\r\nThe output of your script was:\r\n {1}' +
                '\r\nFeedback:\r\n {2}' +
                '\r\nAny errors are listed below:\r\n {3}'
            ).format(
                Spoints,
                Soutput.replace('\n','\r\n'),
                Sfeedback.replace('\n','\r\n'),
                Serror.replace('\n','\r\n')
                
            ))
        
        # Show the results
        print ( 
            (
                '\nPoints received: {0}' +
                '\nClean exit?: {1}' +
                '\nOutput of script:\n {2}' +
                '\nErrors (if any):\n {3}' +
                '\nFeedback:\n {4}'
            ).format(
                Spoints,
                Scleanexit,
                Soutput,
                Serror,
                Sfeedback
            )
        )
        
        return Spoints


#TestAR10366_Bulk()