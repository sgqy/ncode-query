#!/usr/bin/env python3

import sys
import ncode_query

def main(argc, argv):
    if argc != 3:
        print(ncode_query.query_global_help)
        exit()
    print(ncode_query.search_global(argv[1], argv[2]))
    
main(len(sys.argv), sys.argv)
