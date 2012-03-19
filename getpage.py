#!/usr/bin/env python

import os
import sys
import subprocess

def getpage(url):
    return subprocess.check_output(['casperjs', '_getpage.js', url])

def main():
    if len(sys.argv) != 3:
        print "usage: %s <url> <dest>" % sys.argv[0]
        sys.exit(-1)

    url, dest = sys.argv[1:]

    # TODO - write out as it gets here
    output = getpage(url)

    if dest == '-':
        print output
    else:
        with open(dest, 'w+') as f:
            f.write(output)

if __name__ == '__main__':
    main()
