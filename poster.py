"""
POST to URLs
"""
import optparse
import urllib2
import sys

parser = optparse.OptionParser(
    usage="%prog URL var=value var=@file ...")
parser.add_option(
    '-r', '--view-result',
    dest="view_result",
    action="store_true",
    help="View the result of the POST")

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    options, args = parser.parse_args(args)
    url = args[0]
    vars = []
    has_file = False
    for arg in args[1:]:
        if '=' not in arg:
            print 'Bad argument: %r' % arg
            sys.exit(2)
        name, value = arg.split('=', 1)
        vars.append((name, value))
        if value.startswith('@'):
            has_file = True
    if has_file:
        content_type = 'multipart/form-data'
        body = make_file_body(vars)
    else:
        content_type = 'application/x-www-form-urlencoded'
        body = make_simple_body(vars)
        
            
    
    
