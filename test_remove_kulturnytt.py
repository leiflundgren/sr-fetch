#!/usr/bin/python
# -*- coding: latin-1 -*-

from remove_kulturnytt import RemoveKulturnytt
import os, sys
import unittest
from datetime import timedelta
import dateutil.parser

class TestRemoveKulturnytt(unittest.TestCase):
    def setUp(self):
        return super(TestRemoveKulturnytt, self).setUp()

    def assertSequenceEqual(self, it1, it2):
        if it1 is None:
            self.assertIsNone(it2)
        if it2 is None:
            self.assertIsNone(it1)
        l1 = len(it1)
        l2 = len(it2)
        if l1 != l2:
            self.fail('Different length of it1(%d) and it2(%d)' % (l1, l2) )

        for i in range(0, l1-1):
            self.assertEqual(it1[i], it2[i])

    def test_misc(self):

        dt0 = timedelta()
        dt1 = timedelta(minutes=1)
        dt2 = timedelta(minutes=2)


        self.assertEqual(dt1, dt0+dt1)
        self.assertEqual(timedelta(minutes=3), dt1+dt2)



    def test_datetime(self):
        print 'test_datetime'

        d1 = '2013-06-10T17:00:00+0200'
        d2 = dateutil.parser.parse(d1)
        print d1
        print d2

        time = '17:00:00'
        tstr = '%sT%s+0200' % ('2013-07-04', time)

        dt = dateutil.parser.parse(tstr)
        print dt

        print dt.strftime('%Y-%m-%dT%H:%M:%S%z')


        pass


    def test_argparse(self):
        rkn = RemoveKulturnytt.parse(['-y', 'lexsommar-example.m4a'])
        self.assertTrue(rkn.overwrite)
        self.assertEqual(['lexsommar-example.m4a'], rkn.filenames)

        rkn = RemoveKulturnytt.parse(['lexsommar-example.m4a'])
        self.assertFalse(rkn.overwrite)
        self.assertEqual(['lexsommar-example.m4a'], rkn.filenames)
        
        #try:
        #    rkn = RemoveKulturnytt.parse(['-y'])
        #    self.fail('There should have been some sort of parse-error here!')
        #except:
        #    pass
        
        #try:
        #    rkn = RemoveKulturnytt.parse()
        #    self.fail('There should have been some sort of parse-error here!')
        #except:
        #    pass

    def test_read_metadata(self):
        rkn = RemoveKulturnytt('Lexsommar 2000-00-00 Not really a real episode.m4a', False, 8, False)
        rkn.read_metadata()
        self.assertEqual(timedelta(hours=1,minutes=59,seconds=1), rkn.duration)

    def test_build_new_name(self):
        rkn = RemoveKulturnytt.from_argv(['-y', 'Lexsommar 2000-00-00 Not really a real episode.m4a'])
        self.assertEqual('Lexsommar 2000-00-00a Not really a real episode.m4a', rkn.build_new_name('a'))
        self.assertEqual('Lexsommar 2000-00-00b Not really a real episode.m4a', rkn.build_new_name('b'))

        part_a = rkn.command_line_part_a()
        expect_a = ['ffmpeg', '-acodec', 'copy', '-i', 'Lexsommar 2000-00-00 Not really a real episode.m4a', '-vn', '-t', '1:06:30', 'Lexsommar 2000-00-00a Not really a real episode.m4a']

        part_b = rkn.command_line_part_b()
        expect_b = ['ffmpeg', '-acodec', 'copy', '-i', 'Lexsommar 2000-00-00 Not really a real episode.m4a', '-vn', '-ss', '1:14:30', 'Lexsommar 2000-00-00b Not really a real episode.m4a']

        # print part_a
        # print expect_a

        # print part_b
        # print expect_b
        print ''
        self.assertSequenceEqual(expect_a, part_a)
        self.assertSequenceEqual(expect_b, part_b)

if __name__ == '__main__':
    print "TestRemoveKulturnytt::main"
    unittest.main() 
