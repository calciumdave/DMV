#!/usr/bin/env python

import re

s = re.compile('[a-zA-Z]+')
ss = 'today is a good day'

result = s.split(ss)

for item in result:
    print item
