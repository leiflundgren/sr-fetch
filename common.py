
# -*- coding: iso-8859-1 -*-


import sys
import os
import subprocess
import argparse
import datetime
import warnings
import re
import unittest

import email.utils
import time

tracelevel = 4
log_handle = None

def trace(level, *args):
    def mystr(thing):
        if isinstance(thing, (list, tuple)):
            msg = []
            prefix = ''

            if len(thing) <= 4:
               separator = ', '
            else:
               separator = (os.linesep+"   ")
               prefix = separator

            for s in thing:
                msg += [mystr(s)]
            return prefix + separator.join(msg)

        elif isinstance(thing, datetime.datetime):
            return thing.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(thing, datetime.date):
            return thing.strftime("%Y-%m-%d")
        #elif isinstance(thing, bytes):
        #    return bytes.decode('utf-8')
        else:
            try:
                return str(thing)
            except UnicodeEncodeError:
                return str(thing).encode('ascii', 'ignore')
            except ex as Exception:
                return 'Failed to format thing as string caught ' + str(ex)

    #if tracelevel < level:
    #    return

    msg = datetime.datetime.now().strftime("%H:%M:%S: ")
    for count, thing in enumerate(args):
        msg += mystr(thing)

    msg = msg.rstrip()
    handle = sys.stderr if log_handle is None else log_handle

    try:
        print(msg, file=handle)
    except UnicodeEncodeError:
        print(msg.encode('cp850', errors='replace'), file=handle)

def pretty(value,htchar="\t",lfchar="\n",indent=0):
  if type(value) in [dict]:
    return "{%s%s%s}"%(",".join(["%s%s%s: %s"%(lfchar,htchar*(indent+1),repr(key),pretty(value[key],htchar,lfchar,indent+1))for key in value]),lfchar,(htchar*indent))
  elif type(value) in [list,tuple]:
    return (type(value)is list and"[%s%s%s]"or"(%s%s%s)")%(",".join(["%s%s%s"%(lfchar,htchar*(indent+1),pretty(item,htchar,lfchar,indent+1))for item in value]),lfchar,(htchar*indent))
  else:
    return repr(value)


def run_child_process(cmd, alt_path=None, get_stdout=True, get_stderr=True):
    """Start a child-process. Run it passing stdout-data to the main stdout."""

    trace(6, 'Calling ', cmd, " alt_path:", alt_path)
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)

    
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = p.communicate()
    except OSError as e:
        if e.errno != 2 or alt_path is None:
            raise e
        cmd[0] = os.path.join(alt_path, os.path.basename(cmd[0]))
        return run_child_process(cmd, None)

    if p.returncode == 0:
        trace(6, 'process terminated successfully')
    else:
        trace(4, 'process failed ' + str(p.returncode) + "\r\n" + stdout_data + stderr_data)

    trace(7, 'stdout:\r\n' + stdout_data)
    trace(7, 'stderr:\r\n' + stderr_data)
    
    data = ''
    if get_stdout: data += stdout_data 
    if get_stderr: data += stderr_data
    return (p.returncode, data)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    swe_weekdays = {'m&#229;ndag':0, 'måndag':0, 'tisdag':1, 'onsdag':2, 'torsdag':3, 'fredag':4, 'l#246;ndag':5, 'l#214;rdag':5, 'lördag':5, 'lördag':5, 's#246;ndag':6, 's#214;ndag':6, 'söndag':6, 'söndag':6 }


# make sure januari is month 1
swe_months = [None, 'januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti', 'september', 'oktober', 'november', 'december']

def is_swe_month(x):
    return parse_swe_month(x) >= 0

def is_swe_weekday(x):
    return parse_swe_weekday(x) >= 0

def parse_swe_month(x):
    try:
        return swe_months.index(x.lower())
    except ValueError:
        return -1


def parse_swe_weekday(x):
    return swe_weekdays.get(x.lower(), -1)

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

def combine_http_path(x, y):
    return x.rstrip('/') + '/' + y.lstrip('/')

""" 
    Parses a datetime like 2000-01-01T23:45:00    
    Timezone is ignored  
        2016-05-25T09:08:00+02:00
"""
def parse_datetime(s):
    def parse_without_timezone(s):
        try:
            if len(s) > 9 and ( s[8] == 'T' or s[10] == 'T'):
                return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            pass
        return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    
    trace(9, 'parse_datetime(' + s + ')')
    if re.match('.*[\+\-]\d\d\:\d\d$', s):
        raise ValueError('common.parse_datetime doesnt support timezones')
    return parse_without_timezone(s)

def parse_datetime_to_rfc822(s):
    if re.match('.*[\+\-]\d\d\:\d\d$', s):
        tz = s[-6:-3] + s[-2:] # timezone, without colon
        s = s[:-6]
    elif s[-1] == 'Z': #  "2011-08-12T20:17:46Z" is Zulu-time
        tz = 'GMT'
        s = s[:-1]
    else:
        tz = 'GMT'
    dt = parse_datetime(s)
    #return dt
    rfc822 = email.utils.format_datetime(dt)
    rfc822 = rfc822[:-5] + tz # replace -0000 with timezone
    trace(9, 'parse_datetime_to_rfc822("' + s + '") -> ' + str(rfc822))
    return rfc822


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

if __name__ == '__main__':
    print(sys.argv)
    print('hello world')
    time.sleep(4)
    tracelevel = 8

    class TestCommon(unittest.TestCase):
        def test_parse_datetime(self):
            trace(4, 'test_parse_datetime testing...')
            t = parse_datetime('2000-01-01T23:45:00')
            self.assertEqual(datetime.datetime(2000,1,1,23,45,0), t)

            t = parse_datetime('2000-01-01 23:45:00')
            self.assertEqual(datetime.datetime(2000,1,1,23,45,0), t)

            #t = parse_datetime('2000-01-01T23:45:00+02:00')
            #self.assertEqual(datetime.datetime(2000,1,1,23,45,0), t)

            #t = parse_datetime('2000-01-01 23:45:00+02:00')
            #self.assertEqual(datetime.datetime(2000,1,1,23,45,0), t)        
            trace(4, 'test_parse_datetime passed')

        def test_parse_datetime_rfc822(self):
            trace(4, 'test_parse_datetime_rfc822 testing...')
            t = parse_datetime_to_rfc822('2000-01-01T23:45:00')
            self.assertEqual('Sat, 01 Jan 2000 23:45:00 GMT', t)

            t = parse_datetime_to_rfc822('2000-01-01 23:45:00')
            self.assertEqual('Sat, 01 Jan 2000 23:45:00 GMT', t)

            t = parse_datetime_to_rfc822('2000-01-01T23:45:00+02:00')
            self.assertEqual('Sat, 01 Jan 2000 23:45:00 +0200', t)

            t = parse_datetime_to_rfc822('2000-01-01 23:45:00+02:00')
            self.assertEqual('Sat, 01 Jan 2000 23:45:00 +0200', t)

            t = parse_datetime_to_rfc822('2016-09-17T12:47:41Z')
            self.assertEqual('Sat, 17 Sep 2016 12:47:41 GMT', t)
            
            
            trace(4, 'test_parse_datetime_rfc822 passed')
        pass


   
    trace(4, 'Running common-unitttests')
    sys.exit(unittest.main(argv=['-v']))
