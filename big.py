#!/usr/bin/env python3

import sys
import ncode_query

def main(argc, argv):
    if argc != 3:
        print(ncode_query.big_query_help)
        exit()
    ncode_query.proc_g(argv[1], argv[2])
    
main(len(sys.argv), sys.argv)
