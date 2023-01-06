#!/usr/bin/python3

import sys
import argparse
import subprocess
import re
import os
from datetime import timedelta
import time
import unittest
import glob
#import dateutil.parser
import common

def isEmpty(value):
    return value is None or len(value) == 0


class SrSetMetadata:
    """Set metadata of m4a from filename"""

    def __init__(self, filename, overwrite, tracelevel, metadata_changer):
        self.filename = filename
        self.overwrite = overwrite
        self.tracelevel = tracelevel
        common.tracelevel = tracelevel
        self.metadata_changer = metadata_changer if not metadata_changer is None else 'ffmpeg'

        self.trace(4, 'SrSetMetadata filename=%s  overwrite=%s  tracelevel=%d  AtomicParslay="%s"' % (self.filename, self.overwrite, self.tracelevel, self.metadata_changer) )
        
    def trace(self, level, msg):
        common.trace(level, msg)

    def parse_filename(self):
        self.trace(6, 'Parsing ' + self.filename)

        m = re.match('^(.*) (\d\d\d\d\-\d\d?\-\d\d?)([a-c]?) +([^ ].*)\.m4a$', self.filename)
        
        if m is None:
            m = re.match('^(.*) (\d\d\d\d\d\d)([a-c]?) +([^ ].*)\.m4a$', self.filename)

        if m is None:
            m = re.match('^(.+) (\d\d\d\d\d\d)([a-c]?)( +[^ ].*)?\.m4a$', self.filename)

        if m is None:
            raise ValueError('Bad format of file "' + self.filename + '" doesn\'t match regex')

        # self.trace(7, 'match-parts ' + str(list(m.group[1:])))

        self.progname = m.group(1).strip()
        if self.progname == 'Lexsommar':
            self.artist = 'Lex'
        elif self.progname == 'Lordagsmorgon':
            self.artist = 'Eric Schult'
        else:
            self.artist = self.progname

            
            
        self.date = m.group(2)
        self.part = m.group(3)
        self.desc = m.group(4).strip()

       
    def metadata_commandline(self):
        desc = self.desc
        if desc.endswith('..') and not desc.endswith('...'):
            desc += '.'
        date = self.date
        
        if self.progname == 'Lexsommar':
            timeofday = '17:00:00' if self.part != 'b' else '18:10:00'
            date = '%sT%s' % (date, timeofday)

        self.trace(7, "self.metadata_changer: " + self.metadata_changer)
        if self.metadata_changer.index('ffmpeg') >= 0:
            return self.ffmpeg_commandline(desc, date)
        else:
            return self.atomic_parsly_commandline(desc, date)

    def atomic_parsly_commandline(self, desc, date):

        return [ self.metadata_changer, self.filename, '--artist', self.artist, '--album', self.progname, '--title', self.date + self.part + ' ' + desc, '--year', date ]
       
    def ffmpeg_commandline(self, desc, date):

        fileName, fileExtension = os.path.splitext(self.filename)
        return [ 
            self.metadata_changer, 
            '-i', self.filename, 
            '-vn', '-acodec', 'copy', 
            '-metadata', 'artist=' + self.artist, 
            '-metadata', 'album='+ self.progname, 
            '-metadata', 'title='+ self.date + self.part + ' ' + desc, 
            '-metadata', 'year=' + date,
            '-metadata', 'network="Sveriges Radio"',
            '-y',
			fileName + '-temp-4711' + fileExtension]


    def rename_parsley_output(self):
        self.parse_filename()
        temp_pattern = '%s %s%s %s-temp-*.m4a' % (self.progname, self.date, self.part, self.desc)
        temp_files = glob.glob(temp_pattern)

        if len(temp_files) == 0:
            self.trace(6, 'No tempfiles found for ' + self.filename)
            return None
        if len(temp_files) > 1:
            self.trace(3, 'Found %d found for %s. Using first %s' % (len(temp_files), self.filename, temp_files[0]))

        self.trace(4, 'Deleting "%s" and replacing with parsley output "%s"' % (self.filename, temp_files[0]))
        os.remove(self.filename)
        os.rename(temp_files[0], self.filename)
        
    def touch_creation_time(self):
        self.parse_filename()
        timeofday = '17:00:00' if self.part != 'b' else '18:10:00'

        tstr = '%sT%s' % (self.date, timeofday)

        dt = common.parse_datetime(tstr)
        new_mtime = time.mktime(dt.timetuple())
        self.trace(7, 'Setting modification time to ' + str(dt) + ' (' + str(new_mtime) + ' seconds since 1970)')


        st = os.stat(self.filename)
        atime = st.st_atime #access time
        mtime = st.st_mtime #modification time


        #modify the file timestamp
        os.utime(self.filename,(atime,new_mtime))

    def call_cmd(self):
        cmd = self.metadata_commandline()
        self.trace(5, 'Calling ' + str(cmd))
        try:
            subprocess.call(cmd)
            return True
        except OSError as e:
            if e.errno == 2:
                return False
            raise

    def change_metadata(self):
        try:
            if self.call_cmd():
                self.trace(7, 'metadata changed without error')
                return True

            dir = os.path.dirname(sys.argv[0])
            self.metadata_changer = os.path.join(dir, self.metadata_changer)
            self.trace(7, 'Changing metadata-changer to ' + self.metadata_changer)            
            if self.call_cmd():
                self.trace(7, 'metadata changed without error')
                return True

            self.trace(3, "Failed to find metadata_changer, metadata not changed")
            return False

        except: # catch *all* exceptions
            e = sys.exc_info()[0]
            self.trace(2, 'failed to called metadata changer: ' + str(e))
            return False

    def main(self):
        self.parse_filename()

        self.change_metadata()

        if self.overwrite:
            self.rename_parsley_output()
        self.touch_creation_time()


class TestSrSetMetadata(unittest.TestCase):
    def setUp(self):
        return super(TestSrSetMetadata, self).setUp()

    def test_misc(self):

        dt0 = timedelta()
        dt1 = timedelta(minutes=1)
        dt2 = timedelta(minutes=2)


        self.assertEqual(dt1, dt0+dt1)
        self.assertEqual(timedelta(minutes=3), dt1+dt2)

    def test_parse_filename(self):
        testcases = ( 
            # orig, name, data, a/b-field, desc
           (    'Lexsommar 2000-00-00 Not really a real episode.m4a', 
                ['AtomicParsley/AtomicParsley', 'Lexsommar 2000-00-00 Not really a real episode.m4a', '--artist', 'Lex', '--album', 'Lexsommar', '--title', '2000-00-00 Not really a real episode', '--year', '2000-00-00T17:00:00Z'],
                ('Lexsommar', '2000-00-00', '', 'Not really a real episode') 
           ),
           (    'Lexsommar 2000-00-00a Not really a real episode.m4a', 
                ['AtomicParsley/AtomicParsley', 'Lexsommar 2000-00-00a Not really a real episode.m4a', '--artist', 'Lex', '--album', 'Lexsommar', '--title', '2000-00-00a Not really a real episode', '--year', '2000-00-00T17:00:00Z'],
                ('Lexsommar', '2000-00-00', 'a', 'Not really a real episode') 
           ),
           (    'Lexsommar 2000-00-00a Not really a real episode.m4a', 
                ['AtomicParsley/AtomicParsley', 'Lexsommar 2000-00-00a Not really a real episode.m4a', '--artist', 'Lex', '--album', 'Lexsommar', '--title', '2000-00-00a Not really a real episode', '--year', '2000-00-00T17:00:00Z'],
                ('Lexsommar', '2000-00-00', 'a', 'Not really a real episode') 
           ),
        ) 

        for t in testcases:
            expected = t[2]

            ssm = SrSetMetadata(t[0], True, 8, 'AtomicParsley/AtomicParsley')
            ssm.parse_filename()
            self.assertEqual(expected[0], ssm.progname)
            self.assertEqual('Lex', ssm.artist)
            self.assertEqual(expected[1], ssm.date)
            self.assertEqual(expected[2], ssm.part)
            self.assertEqual(expected[3], ssm.desc)

            expected = t[1]
            cmd = ssm.atomic_parsly_commandline()
            self.assertEquals(expected, cmd)


if __name__ == '__main__':

    print 'argv: ' + str(sys.argv[1:])
    #sys.exit(1)

    for a in sys.argv:
        if a == '--unittest':
            sys.argv = ['-v']
            sys.exit(unittest.main())

    parser = argparse.ArgumentParser(description='My favorite argparser.')
    parser.add_argument('-y', '--overwrite', help='Overwrite exisitng files', action='store_true', default=False, required=False, dest='overwrite')
    parser.add_argument('-l', '--tracelevel', help='Verbosity level 1 is important like error, 9 is unneeded debuginfo', default=4, type=int)
    parser.add_argument('-m', '--metadata', help='Location of metadata program. Supported ffmpeg and AtomicParsley', dest='metadata_changer', default='ffmpeg')
    parser.add_argument('filenames', metavar='filename.m4a', help='filename to remove kulturnytt from', nargs='+')

                    
    args = parser.parse_args()

    for f in args.filenames:
        SrSetMetadata(f, args.overwrite, args.tracelevel, args.metadata_changer).main()
       





