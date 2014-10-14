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
# - type/signature (where it's valid, how many arguments does it have, does it accept a block?)
# - (function pointer) that handles the arguments to this directive (usually a simple set conf slot)
# - conf level (unnecessary in most cases, type handles it)
# - offset (like conf level)
# - post processing handler (function pointer)

def get_exps():
    if using_re2:
        import sys
        import StringIO
        
        olds = sys.stdout
        sys.stdout = StringIO.StringIO()

    exp_command = re.compile(r"""{\s*?
                ngx_string\("(?P<name>[a-z0-9_]+)"\)\s*,\s*
                (?P<signature>[A-Z0-9_]+(?:\s*\|\s*[A-Z0-9_]+)*)\s*,
                (?P<setter>(?:\([^)]*\)|[^,()])+),\s*
                (?P<conf_level>(?:\([^)]*\)|[^,()])+),\s*
                (?P<offset>(?:\([^)]*\)|[^,()])+),\s*
                (?P<postproc>(?:\([^)]*\)|[^,()])+)
                }""", re.MULTILINE | re.VERBOSE)

    exp_def = re.compile(r"#define (?P<def>NGX_[^ ]+)")

    if using_re2:
        sys.stdout = olds
    return {'command': exp_command, 'def': exp_def}

def parse_file(path, exp):
    with open(path) as f:
        for m in exp.finditer(f.read()):
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
    

    class Directive(object):
        def __init__(self, name, signature, setter, conf_level, offset, postproc):
            self.name = name
            self.signature = signature
            self.setter = setter
            self.conflevel = conf_level
            self.offset = offset
            self.postproc = postproc

        def __str__(self):
            return "%s (%s)" % (self.name, self.signature)

    class Def(object):
        def __init__(self, name):
            self.name = name


    directives = []
    defs = set(['NULL', 'NGX_OFF_T_LEN', '0', '1'])

    exps = get_exps()

    for i in os.walk(args.nginx_source, followlinks=True):
        for f in i[2]:
            fn = "%s/%s" % (i[0], f)
            print("Parsing %s" % fn)
            for conf in parse_file(fn, exps['command']):
                conf = {k:v.strip() for k,v in conf.items()}
                directives.append(Directive(**conf))
            for def_ in parse_file(fn, exps['def']):
                defs.add(def_['def'].strip())

    for d in directives:
        for s in d.signature.split('|'):
            if s.strip() not in defs:
                print("uh-oh: %s" % s)

        # TODO: build list of directive dependencies
        #       generate pyparsing grammar



 
