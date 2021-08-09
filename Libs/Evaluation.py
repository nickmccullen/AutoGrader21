import sys
sys.path.append('.') #may not be needed

class Evaluation:
    """ An abstract class that helps define and use evaluation classes """
    #def __init__(self):
    # The plugin type is a unique identifier for new plugins. This MUST be set in new plugins.
    # TODO: Move the unique identification to the DB
    plugin_type = None

    # The plugin name is a friendly name for the plugin shown in the interface. This MUST be set in new plugins.
    # TODO: Move the plugin name to the DB
    plugin_name = None


    ### Evaluation plugins can modify the following properties, which get returned to the grader ###

    # [FLOAT]: The number of points the student received for their work
    _points_received = 0.0

    # [BOOLEAN]: Whether the student's work exited cleanly or not (can be overridden by the grader)
    _clean_exit = True

    # [STRING]: Any output message from the plugin or student's work that should be displayed to the tutor
    _output_string = ''

    # [STRING]: Any error message from the plugin or student's work that should be displayed to the tutor
    _error_string = ''

    # [STRING]: Any feedback message from the plugin or student's work that should be given for the operation
    _feedback_string = ''
    
    
    ### The mark function below MUST be implemented when a new plugin is created.
    def mark(self, sandbox, *args):
        """ This function should be implemented to mark the student's work, and set values for the properties above """
        raise NotImplementedError('Marking function is not defined for plugin [' + str(self.plugin_type) + ']')

    # Nothing is done with init right now, you're welcome to override it.
    #def __init__(self):
    #    pass
    
    
    ### The functions below this comment MUST NOT be edited when a new plugin is created
    def reset(self):
        # Reset this class when he's loaded
        self._points_received = 0.0
        self._clean_exit = True
        self._output_string = ''
        self._error_string = ''

    def getType(self):
        """ Allows the plugin id to be fetched by the interface and grader. Don't mess with this guy. """
        if self.plugin_type is not None:
            return self.plugin_type
        else:
            raise NotImplementedError('Plugin type is not defined')

    def getName(self):
        """ Allows the plugin name to be fetched by the interface and grader. Don't mess with this guy. """
        if self.plugin_name is not None:
            return self.plugin_name
        else:
            raise NotImplementedError('Plugin name is not defined')

    def getPointsReceived(self):
        if self._points_received is not None:
            return self._points_received
        else:
            raise NotImplementedError('Plugin points received is not set')

    def getCleanExit(self):
        if self._clean_exit is not None:
            return self._clean_exit
        else:
            return False
            # raise NotImplementedError('Plugin clean exit is not set')

    def getOutput(self):
        if self._output_string is not None:
            return self._output_string
        else:
            return None
            # raise NotImplementedError('Plugin output is not set')

    def getError(self):
        if self._error_string is not None:
            return self._error_string
        else:
            return None
            # raise NotImplementedError('Plugin error is not set')

    def getFeedback(self):
        if self._feedback_string is not None:
            return self._feedback_string
        else:
            return None
            # raise NotImplementedError('Plugin feedback is not set')

