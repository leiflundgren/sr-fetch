
# coding: latin-1


import sys
import os
import subprocess
import argparse
import datetime

tracelevel = 4

log_handle = None

def trace(level, *args):
    def mywrite(thing):
        if log_handle is None:
            sys.stdout.write(mystr(thing))
        else:
            print >> log_handle, mystr(thing)

    def mystr(thing):
        try:
            return str(thing)
        except UnicodeEncodeError:
            return unicode(thing).encode('ascii', 'ignore')
<<<<<<< HEAD
=======
        except:
            return unicode(thing).encode('ascii', 'ignore')
>>>>>>> f24de458f1e8aad2b244e44fe9e52b3406ddba8f

    if tracelevel >= level:
        msg = datetime.datetime.now().strftime("%H:%M:%S: ")
        if isinstance(args[0], (list, tuple)):
            for s in args[0]:
                msg += mystr(s)
        else:
            for count, thing in enumerate(args):
                msg += mystr(thing)                
<<<<<<< HEAD
=======
        msg += "\n"
>>>>>>> f24de458f1e8aad2b244e44fe9e52b3406ddba8f
        mywrite(msg)
        return msg

    return 'not logged'

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
    trace(6, 'process terminated ' + str(p.returncode))
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
    return res

"""" Parses a datetime like 2000-01-01T23:45:00
Timezone is ignored """
def parse_datetime(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

def format_datetime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S%z')
