#!/usr/bin/env python3

import sys
import ncode_query

def main(argc, argv):
    if argc != 3:
        print(argv[0] + ' <list> <type>')
        print('type: s = single')
        print('      b = bunch')
        exit()

    fs = open(argv[1], 'rb')
    ls = fs.read().decode('utf8').split('\n')
    fs.close()
    
    if argv[2] == 's':
        print(ncode_query.search_file_local_order(ls))
    elif argv[2] == 'b':
        print(ncode_query.search_file_remote_order(ls))

main(len(sys.argv), sys.argv)
