#!/usr/bin/python

import sys
import argparse
import subprocess
import re
import os
import common
from datetime import timedelta

# Kulturnytt starts at 3990 and ends 4470
# ffmpeg -i Lexsommar 2013-07-10 Regn, Regn, Regn.m4a -t 3990 -acodec copy Lexsommar 2013-07-10a Regn, Regn, Regn.m4a
# ffmpeg -i Lexsommar 2013-07-10 Regn, Regn, Regn.m4a -ss 4470 -acodec copy Lexsommar 2013-07-10b Regn, Regn, Regn.m4a

def isEmpty(value):
    return value is None or len(value) == 0


class RemoveKulturnytt:
    """My attempt to remove a certain part of the file-contents. With some sanity-safty"""

    def __init__(self, filename, overwrite, tracelevel, deleteMaster):
        self.filename = filename
        self.overwrite = overwrite
        self.tracelevel = tracelevel
        self.deleteMaster = deleteMaster
        
        common.tracelevel = tracelevel

        # print 'overwrite = ' + str(self.args.overwrite)
        # print 'filename = ' + str(self.args.filename)

        self.ffmpg_cmd_base = ['ffmpeg', '-v', str(max(0,tracelevel-6)), '-i', self.filename, '-acodec', 'copy']
        

    def read_metadata(self):
        proc = subprocess.Popen(['ffprobe', self.filename], stderr=subprocess.PIPE, shell=False)
        self.trace(6, 'Reading metadata from ' + self.filename)

        self.duration = timedelta()
        data = proc.stderr.read()
        self.trace(8, 'read data:\n' + data)
        
        input_begin = data.find('Input #0')

        if input_begin < 0:
            self.trace(3, 'ffprobe didn\'t find any streams! ' + self.filename)
            return

        input_end = data.find('Input #', input_begin+5)
        if input_end < 0:
            input_end = len(data)

        dur_pos = data.find('Duration:', input_begin, input_end)
        if dur_pos < 0:
            self.trace(3, 'ffprobe didn\'t find duration of stream #0 between ' + str(input_begin) + ' to ' + str(input_end))
            return

        dur_eol = data.find('\n', dur_pos)
        dur_line = data[dur_pos:dur_eol]
        # print dur_line

        self.trace(7, dur_line)

        key = 'Duration:'
        pos = dur_line.index(key) + len(key)
        endp = dur_line.index(',', pos)
        # print 'pos:' + str(pos) + '  endp:' + str(endp)
        sdur = dur_line[pos:endp].strip()

        parts = re.compile('[:\.]').split(sdur)
        # print 'sdur:' + sdur + ' parts:' + str(parts)
        self.duration = timedelta()
        i = 0
        if len(parts)>=3:
            self.duration = self.duration + timedelta(hours=int(parts[i]))
            i = i+1
        if len(parts)>=2:
            self.duration = self.duration + timedelta(minutes=int(parts[i]))
            i = i+1
        if len(parts)>=1:
            self.duration = self.duration + timedelta(seconds=int(parts[i]))
            i = i+1

        try:
            proc.terminate()                      # Kill the process
        except:
            pass

    def is_supported_show(self):
        lower_filename = self.filename.lower()
        if lower_filename.find('lexsommar') >= 0:
            return True

        if lower_filename.find('p2') >= 0 and lower_filename.find('hemvag') >= 0:
            return True
        
        # doesn't seems to be Lexsommar, so no kulturnytt....
        self.trace(6, 'Target file "%s" seems like not a supported kulturnytt-show...' % (self.filename))
        return False

    # An episode with kulturnytt is typically 1:59:01, 7141 seconds.
    def seems_like_kulturnytt_is_still_here(self):
        if not self.is_supported_show():
            return False


        long_enough = False
            
        try:
            long_enough = self.duration >= timedelta(hours=1, minutes=59)
        except:
            self.read_metadata()
            long_enough = self.duration >= timedelta(hours=1, minutes=59)
            
        if not long_enough:
            self.trace(6, 'Target file "%s" seems already trimmed. Duration was only %s' % (self.filename, str(self.duration)))
        return long_enough
        
        
    def build_new_name(self, part_id):
        re_name = re.compile('^(.* \d\d\d\d\-\d+\-\d+) +(.*\.m4a)$')
        m = re_name.match(self.filename)
        if m is None:
            raise ValueError('Failed to build new name from original "%s". Regex didn\'t match.' % (self.filename))
        return '%s%s %s' % (m.group(1).strip(), part_id, m.group(2).strip()) 

    def part_1_end(self):
        #return str(  3990)
        return timedelta(hours=1, minutes=6, seconds=30)

    def kulturnytt_length(self):
        return timedelta(minutes=8)

    def part_2_begin(self):
        return self.part_1_end() + self.kulturnytt_length()

    def command_line_part_a(self):
        # ffmpeg -acodec copy -i Lexsommar 2013-07-10 Regn, Regn, Regn.m4a -t 3990 Lexsommar 2013-07-10a Regn, Regn, Regn.m4a
        return self.ffmpg_cmd_base + ['-vn', '-t', str(self.part_1_end()), self.build_new_name('a')]
        
    def command_line_part_b(self):
        # ffmpeg -acodec copy -i Lexsommar 2013-07-10 Regn, Regn, Regn.m4a -ss 4470 Lexsommar 2013-07-10b Regn, Regn, Regn.m4a
        return self.ffmpg_cmd_base + ['-vn', '-ss', str(self.part_2_begin()), self.build_new_name('b')]

    
    def parse_filename(self):
        self.trace(6, 'Parsing ' + self.filename)

        m = re.match('^(.*) (\d\d\d\d\-\d\d?\-\d\d?)([a-c]?) +([^ ].*)\.m4a$', self.filename)

        self.progname = m.group(1).strip()
        if self.progname == 'Lexsommar':
            self.artist = 'Lex'
        else:
            self.artist = self.progname

        self.date = m.group(2)
        self.part = m.group(3)
        self.desc = m.group(4)


    def del_bigfile_if_split(self, a_part, b_part):
        self.parse_filename()
        if self.part != '':
            self.trace(7, "The file " + self.filename + " is not a master-file. Ignoring")
            return None
        
        if not os.path.exists(a_part) or not os.path.exists(b_part):
            self.trace(4, "Master " + self.filename + " was missing a/b part. Not deleting")
            self.trace(6, 'exists(%s)->%s  exists(%s)->%s' % ( a_part, os.path.exists(a_part), b_part, os.path.exists(b_part) ))
            return None
        
        self.trace(2, 'Deleting master ' + self.filename + ' since parts already exists')
        os.remove(self.filename)

        return None


    def trace(self, level, msg):
        common.trace(level, msg)

    @staticmethod
    def parse(x):
        parser = argparse.ArgumentParser(description='My favorite argparser.')
        parser.add_argument('-y', '--overwrite', help='Overwrite exisitng files', action='store_true', default=False, required=False, dest='overwrite')
        parser.add_argument('--delete-master', help='Delete the masterfile once splitted', action='store_true', default=False, required=False, dest='deleteMaster')
        parser.add_argument('filenames', metavar='file', nargs='+', help='filename to remove kulturnytt from')
        parser.add_argument('-l', '--tracelevel', help='Verbosity level 1 is important like error, 9 is unneeded debuginfo', default=4, type=int)
                
        return parser.parse_args(x)

    @staticmethod
    def from_argv(argv):
        args = RemoveKulturnytt.parse(argv)
        if len(args.filenames) > 1:
            raise ValueError('Only one filename might be supplied in this method')
        return RemoveKulturnytt(args.filenames[0], args.overwrite, args.tracelevel, args.deleteMaster)

    """Performs the work. Returns list of the newly created files. (None if nothing was done.)"""
    def main(self):
        self.trace(5, 'Processing ' + self.filename)

        if not self.seems_like_kulturnytt_is_still_here():
            return None            

        a_part = self.build_new_name('a')
        b_part = self.build_new_name('b')

        if not self.overwrite and ( os.path.exists(a_part) or os.path.exists(b_part) ):
            if self.deleteMaster:
                self.del_bigfile_if_split(a_part, b_part)
                
            if os.path.exists(a_part):
                self.trace(4, 'Target file "%s" already exists. Aborting!' % (a_part) )
                return None
            if os.path.exists(b_part):
                self.trace(4, 'Target file "%s" already exists. Aborting!' % (b_part) )
                return None


        self.trace(3, 'Calling ffmpeg to extract the file-parts')
        cmd1 = self.command_line_part_a()
        cmd2 = self.command_line_part_b()

        (res1, data1) = common.run_child_process(cmd1)
        (res2, data2) = common.run_child_process(cmd2)

        if self.deleteMaster:
            self.del_bigfile_if_split(a_part, b_part)

        return [a_part, b_part]


if __name__ == '__main__':
    args = RemoveKulturnytt.parse(None)
    # print 'filename = ' + str(self.args)
    for f in args.filenames:
        RemoveKulturnytt(f, args.overwrite, args.tracelevel, args.deleteMaster).main()
       





