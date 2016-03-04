C_HEADER = '\033[95m'
C_BLUE = '\033[94m'
C_GREEN = '\033[92m'
C_SOMEOTHER = '\033[93m'
C_RED = '\033[91m'
C_ENDC = '\033[0m'
C_BOLD = '\033[1m'
C_UNDERLINE = '\033[4m'

def colour_str(col, s):
    return col + s + C_ENDC
    