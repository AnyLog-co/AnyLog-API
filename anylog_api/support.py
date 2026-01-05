from enum import Enum

class ListCommands:
    """
    help with function information
    """
    def list_commands(self):
        """
        provide docstring / help for functions
        """
        return {
            name: getattr(self, name).__doc__
            for name in dir(self)
            if not name.startswith("_") and callable(getattr(self, name))
        }

class ExecMode(Enum):
    EXECUTE = "execute" # execute command
    COMMAND = "command" # return
    HELP = "help" # print command help
