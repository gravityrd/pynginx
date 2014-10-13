#!/usr/bin/env python

try:
    # hg clone https://code.google.com/p/re2/
    import re2 as re
    using_re2 = True
except ImportError:
    # but that's really bad, see
    # http://stackoverflow.com/questions/26210449/why-python-chokes-on-this-regex
    import re
    using_re2 = False

import os.path
import argparse
from pprint import pprint

# http://www.nginxguts.com/2011/09/configuration-directives/
# - name
# - type (where)
# - (function pointer) that handles the arguments to this directive (usually a simple set conf slot)
# - conf level (unnecessary in most cases, type handles it)
# - offset (like conf level)
# - post processing handler (function pointer)

def get_exp():
    if using_re2:
        import sys
        import StringIO
        
        olds = sys.stdout
        sys.stdout = StringIO.StringIO()

    exp = re.compile(r"""{\s*?
                ngx_string\("(?P<name>[a-z0-9_]+)"\)\s*,\s*
                (?P<where>[A-Z0-9_]+(?:\s*\|\s*[A-Z0-9_]+)*)\s*,
                (?P<setter>(?:\([^)]*\)|[^,()])+),\s*
                (?P<conf_level>(?:\([^)]*\)|[^,()])+),\s*
                (?P<offset>(?:\([^)]*\)|[^,()])+),\s*
                (?P<postproc>(?:\([^)]*\)|[^,()])+)
                }""", re.MULTILINE | re.VERBOSE)

    if using_re2:
        sys.stdout = olds
    return exp

exp = get_exp()

def parse_file(path):
    with open(path) as f:
        print(".")
        for m in exp.finditer(f.read()):
            print("-")
            yield m.groupdict()

class Absent(object):
    pass

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("--test", default=Absent(), nargs='+')
    p.add_argument("nginx_source", metavar="nginx-source", help="Path to Nginx src/ dir", nargs="?")
    args = p.parse_args()
    
    if type(args.test) is not Absent:
        print("Parsing %s" % ", ".join(args.test))
        for fn in args.test:
            with open(fn) as f:
                print("\n\n%s\n" % fn)
                for m in exp.finditer(f.read()):
                    pprint(m.groupdict())
        exit(0)
    
    if args.nginx_source is None or not os.path.isdir(args.nginx_source):
        print("Argument must be nginx's src/ dir")
        exit(1)
    

    for i in os.walk(args.nginx_source, followlinks=True):
        for f in i[2]:
            fn = "%s/%s" % (i[0], f)
            print("Parsing %s" % fn)
            for conf in parse_file(fn):
                conf = {k:v.strip() for k,v in conf.items()}
                print("Valid name: %s (%s)" % (conf['name'], conf['where']))
 
