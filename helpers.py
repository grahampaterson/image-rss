import time

# CONSTANTS
# ===================================================
LOG_FILE = 'log.txt'


# FUNCTIONS
# ===================================================

# String -> Write to file, Int
# takes a string and writes it to a predefined file and returns 1 if succesful
def log(string):
    # create file if it doesn't already exist
    try:
        f = open(LOG_FILE, 'a') #opens file with append mode
        current_time = time.ctime()
        # get the filename and function name
        f.write(current_time + ' ' + string + "\n")  # add details to log file imestamped with file name
        return 1
    except:
        return 0
