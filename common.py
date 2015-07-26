
# coding: latin-1


import sys
import os
import subprocess
import argparse
import datetime

tracelevel = 9
log_handle = None

def trace(level, *args):
    def mystr(thing):
        if isinstance(thing, (list, tuple)):
            msg = ''
            for s in thing:
                msg += mystr(s) + ','
            return msg
        else:
            try:
                return str(thing)
            except UnicodeEncodeError:
                return unicode(thing).encode('ascii', 'ignore')
            except ex as Exception:
                return 'Failed to format thing as string caught ' + str(ex)

    if tracelevel < level:
        return

    msg = datetime.datetime.now().strftime("%H:%M:%S: ")
    for count, thing in enumerate(args):
            msg += mystr(thing)

    if log_handle is None:
        print >> sys.stderr, msg.rstrip()
    else:
        print >> log_handle, msg.rstrip()

def pretty(value,htchar="\t",lfchar="\n",indent=0):
  if type(value) in [dict]:
    return "{%s%s%s}"%(",".join(["%s%s%s: %s"%(lfchar,htchar*(indent+1),repr(key),pretty(value[key],htchar,lfchar,indent+1))for key in value]),lfchar,(htchar*indent))
  elif type(value) in [list,tuple]:
    return (type(value)is list and"[%s%s%s]"or"(%s%s%s)")%(",".join(["%s%s%s"%(lfchar,htchar*(indent+1),pretty(item,htchar,lfchar,indent+1))for item in value]),lfchar,(htchar*indent))
  else:
    return repr(value)


def run_child_process(cmd):
    """Start a child-process. Run it passing stdout-data to the main stdout."""

    trace(6, 'Calling ', cmd)
    #res = subprocess.call( cmd, stdout=sys.stdout, stderr=sys.stderr)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout_data = ''
    while p.poll() is None:
        line = p.stdout.readline()
        stdout_data += line
        trace(7, line.strip())
    if p.returncode == 0:
        trace(6, 'process terminated successfully')
    else:
        trace(4, 'process failed ' + str(p.returncode) + "\r\n" + stdout_data )
    
    return (p.returncode, stdout_data)

def is_swe_month(x):
    x = x.lower()
    for m in ['januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti', 'september', 'oktober', 'november', 'december']:
        if x == m:
            return True
    return False

def unescape_html(html):
    res = ''
    last = 0
    while True:
        pos = html.find('&', last)
        if pos < 0:
            res += html[last:]
            break
        res += html[last:pos]
        sc = html.find(';', pos)
        code = html[pos+1: sc]
        # print 'code: ' + code

        if code == '#229' or code == 'aring':
            res += 'a'
        elif code == '#197' or code.lower() == 'aring' and code[0].isupper():
            res += 'A'
        elif code == '#228' or code == 'auml':
            res += 'a'
        elif code == '#196' or code.lower() == 'auml' and code[0].isupper():
            res += 'A'
        elif code == '#246' or code == 'ouml':
            res += 'o'
        elif code == '#214' or code.lower() == 'ouml' and code[0].isupper():
            res += 'O'
        elif code == '#233': # é
            res += 'e'
        elif code == '#225': # á
            res += 'a'
        elif code == '#237': # í
            res += 'i'
        elif code == '#39': # '
            res += ' '
        elif code == '#233': # é
            res += 'e'
            
        else:
            res += '_'

        last = sc+1
    return res.replace(':', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')

"""" Parses a datetime like 2000-01-01T23:45:00
Timezone is ignored """
def parse_datetime(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

def format_datetime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S%z')

def get_el(root, name, ns=None):
    if ns is None:
        key = name
    else:
        if ns[0]!='{': ns = '{' + ns + '}'
        key = ns + name
    
    for child in root:
        if child.tag == key:
            return child
    return None

def is_none_or_empty(s):
    return s is None or isinstance(s, str) and s == ""