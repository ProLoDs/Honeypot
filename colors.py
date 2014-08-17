class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
def print_good(string):
    print bcolors.OKGREEN + string + bcolors.ENDC
def print_fail(string):
    print bcolors.FAIL + string + bcolors.ENDC
def print_warning(string):
    print bcolors.WARNING + string + bcolors.ENDC
def print_debug(string):
    print bcolors.OKBLUE , string , bcolors.ENDC