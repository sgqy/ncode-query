#!/usr/bin/env python3

import get_bookmark
import ncode_query

query = ['R15 Novel:']
r15 = get_bookmark.r15(738439)
query.extend(r15)
query.append('R18 Novel:')
r18 = get_bookmark.r18(304966)
query.extend(r18)

print(ncode_query.search_file_remote_order(query))
