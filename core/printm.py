import sys

def color(color_option):
    """
        Sets global variables for color codes that are used for printing colored text to the terminal.
    """
    global OKGREEN, FAIL, ENDC
    if color_option:
        OKGREEN = FAIL = ENDC = ''
    else:
        OKGREEN = '\033[92m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
    
def pm(**kwargs):
    if kwargs['msn'] == 1:
        print(f"{FAIL}[Error]{ENDC} Skip {kwargs['target']} invalid json" + 
            f"\n{OKGREEN}Help:{ENDC}" + 
            "\n\tUse https://converter.swagger.io/api/convert?url={url}" + 
            "\n\tTo convert yaml to json or update swagger version\n\tAnd try again")

    elif kwargs['msn'] == 2:
        print(f"{FAIL}[Error]{ENDC} Skip {kwargs['target']} status code != 200")
    
    elif kwargs['msn'] == 3:
        print(f"{FAIL}[Error]{ENDC} File {kwargs['target']} Not Found")
        
    elif kwargs['msn'] == 4:
        path_length = len(kwargs['path']) 
        path_space = ""
        if path_length < 60:
            path_space = ' ' * abs(path_length - 60)

        if kwargs['response'].status_code < 299:
            print(
                kwargs['path'] + 
                path_space +
                OKGREEN + 
                f" [Status: {kwargs['response'].status_code}, Method: {kwargs['method'].upper()},Host: {kwargs['host']}]" +
                ENDC)
        else:
            print(
                kwargs['path'] + 
                path_space + 
                FAIL + 
                f" [Status: {kwargs['response'].status_code},Method: {kwargs['method'].upper()},Host: {kwargs['host']}]" + 
                ENDC)
    
    elif kwargs['msn'] == 5:
        sys.stderr.write("""                 __                __   
 .-----.--.--.--|  |--.--.--.-----|  |_ 
 |__ --|  |  |  |     |  |  |     |   _|
 |_____|________|__|__|_____|__|__|____|
              # version 1.0
              # @author alanEG
""")
    elif kwargs['msn'] == 6:
        print(f"{FAIL}[Error]:{OKGREEN} Content-Type {kwargs['contentTypes']} is not supported")