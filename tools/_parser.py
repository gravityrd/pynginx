#!/usr/bin/env python

try:
    # hg clone https://code.google.com/p/re2/
    import re2 as re
except ImportError:
    # but that's really bad, see
    # http://stackoverflow.com/questions/26210449/why-python-chokes-on-this-regex
    import re
import os.path
import argparse
from pprint import pprint

#               (?P<where>(([A-Z0-9_]{1,15})\s{0,50}){0,20}?)\s{0,20},\s*?

# http://www.nginxguts.com/2011/09/configuration-directives/
# - name
# - type (where)
# - (function pointer) that handles the arguments to this directive (usually a simple set conf slot)
# - conf level
# - offset
# - post processing handler (function pointer)


exp = re.compile(r"""{\s*?
              ngx_string\("(?P<name>[a-z0-9_]+?)"\)\s*?,\s*?
              (?P<where>(([A-Z0-9_]+)\s*\|?)+?)\s*?,\s*?
              (?P<bla>[^\n}]+?)\s*?,\s*?
              (?P<bla2>[^\n}]+?)\s*?,\s*?
              (?P<bla3>[^\n}]+?)\s*?,\s*?
              (?P<bla4>[^\n}]+?)\s*?
              }""", re.MULTILINE | re.VERBOSE)

def test():
  
    # https://www.debuggex.com/r/S__vSvp8-LGLuCLQ
    test0 = """
     { ngx_string("off"), NGX_HTTP_REQUEST_BODY_FILE_OFF },
    """
    
    test00 = """
     { ngx_string("off"), NGX_HTTP_REQUEST_BODY_FILE_OFF },
     { ngx_string("on"), NGX_HTTP_REQUEST_BODY_FILE_ON },
    """
    
    test1 = """
     { ngx_string("daemon"),
       NGX_MAIN_CONF|NGX_DIRECT_CONF|NGX_CONF_FLAG,
       ngx_conf_set_flag_slot,
       0,
       offsetof(ngx_core_conf_t, daemon),
       NULL },

    """

    test2 = """
        { ngx_string("server_name"),
          NGX_HTTP_SRV_CONF|NGX_CONF_1MORE,
          ngx_http_core_server_name,
          NGX_HTTP_SRV_CONF_OFFSET,
          0,
          NULL },

        { ngx_string("types_hash_max_size"),
          NGX_HTTP_MAIN_CONF|NGX_HTTP_SRV_CONF|NGX_HTTP_LOC_CONF|NGX_CONF_TAKE1,
          ngx_conf_set_num_slot,
          NGX_HTTP_LOC_CONF_OFFSET,
          offsetof(ngx_http_core_loc_conf_t, types_hash_max_size),
          NULL },

        { ngx_string("types_hash_bucket_size"),
          NGX_HTTP_MAIN_CONF|NGX_HTTP_SRV_CONF|NGX_HTTP_LOC_CONF|NGX_CONF_TAKE1,
          ngx_conf_set_num_slot,
          NGX_HTTP_LOC_CONF_OFFSET,
          offsetof(ngx_http_core_loc_conf_t, types_hash_bucket_size),
          NULL },

        { ngx_string("types"),
          NGX_HTTP_MAIN_CONF|NGX_HTTP_SRV_CONF|NGX_HTTP_LOC_CONF
                                              |NGX_CONF_BLOCK|NGX_CONF_NOARGS,
          ngx_http_core_types,
          NGX_HTTP_LOC_CONF_OFFSET,
          0,
          NULL },

        { ngx_string("default_type"),
          NGX_HTTP_MAIN_CONF|NGX_HTTP_SRV_CONF|NGX_HTTP_LOC_CONF|NGX_CONF_TAKE1,
          ngx_conf_set_str_slot,
          NGX_HTTP_LOC_CONF_OFFSET,
          offsetof(ngx_http_core_loc_conf_t, default_type),
          NULL },

    """

    import time
    b = ""
    for i in test0:
        b += i

        print("trying %s" % b)
        start = time.time()
        matches = exp.finditer(b)
        for m in matches:
            pprint(m.groupdict())
        print("Took %f s" % (time.time() - start))            
    
    
    for i in ["--", test0, test00, test1, test2]:
        matches = exp.finditer(i)
        print("** len: %d" % len(i))
        for m in matches:

            pprint(m.groupdict())
    

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
    p.add_argument("--test", default=Absent(), nargs='?')
    p.add_argument("nginx_source", metavar="nginx-source", help="Path to Nginx src/ dir", nargs="?")
    args = p.parse_args()
    
    if type(args.test) is not Absent:
        if args.test is None:
            test()
        else:
            print("Parsing %s" % args.test)
            buf = ""
            line_no = 0
            with open(args.test) as f:
                for line in f.readlines():
                    buf += line
                    line_no += 1
                    print("-------- %d " % line_no)

                    for m in exp.finditer(buf):
                        print(m)
        exit(0)
    
    if args.nginx_source is None or not os.path.isdir(args.nginx_source):
        print("Argument must be nginx's src/ dir")
        exit(1)
    

    for i in os.walk(args.nginx_source, followlinks=True):
        for f in i[2]:
            fn = "%s/%s" % (i[0], f)
            print("Parsing %s" % fn)
            for conf in parse_file(fn):
                print("Valid name: %s" % conf['name'])

       
