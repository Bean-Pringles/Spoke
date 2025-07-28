import os
from time import gmtime, strftime

def run(args):
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))