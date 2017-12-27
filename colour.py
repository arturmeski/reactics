C_HEADER = '\033[95m'
C_BLUE = '\033[94m'
C_GREEN = '\033[92m'
C_SOMEOTHER = '\033[93m'
C_RED = '\033[91m'
C_ENDC = '\033[0m'
C_BOLD = '\033[1m'
C_UNDERLINE = '\033[4m'

C_MARK_INFO = C_BOLD + "[" + C_GREEN + "*" + C_ENDC + C_BOLD + "]" + C_ENDC
C_MARK_ERROR = C_BOLD + "[" + C_RED + "!" + C_ENDC + C_BOLD + "]" + C_ENDC

def colour_str(col, s):
    return col + s + C_ENDC
    
def green_str(s):
    return C_GREEN + s + C_ENDC
    
def print_error(s):
    print(C_MARK_ERROR + " " + C_RED + s + C_ENDC)

def print_info(s):
    print("[" + colour_str(C_BOLD, "i") + "] {:s}".format(s))

def print_positive(s):
    print("[" + colour_str(C_BOLD, "+") + "] {:s}".format(s))

# EOF
