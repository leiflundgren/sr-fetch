
# -*- coding: utf-8 -*-


import common
import datetime
import unittest
import sys

import sr_helpers 
 
class TestHelpers(unittest.TestCase):
    
    def test_parse_sr_time_string(self):

        base_day = datetime.datetime(2018,12,2)

        self.assertEqual(datetime.datetime(2018,11,29, 17, 6, 0), sr_helpers.parse_sr_time_string('tor 29 nov kl 17:06', base_day))
        self.assertEqual(datetime.datetime(2018,11,29, 17, 6, 0), sr_helpers.parse_sr_time_string('tor 29 nov kl 17.06', base_day))
        self.assertEqual(datetime.datetime(2018,11,29, 17, 6, 0), sr_helpers.parse_sr_time_string('tor 29 nov kl 1706', base_day))
        self.assertEqual(datetime.datetime(2018,11,29, 17, 6, 0), sr_helpers.parse_sr_time_string('tor 29 nov kl 17 06', base_day))

        base_day = datetime.datetime(2015,7,29)
        t = sr_helpers.parse_sr_time_string('klockan 10:03', base_day) # Just check no exception
        self.assertEqual(datetime.datetime(2015,7,29, 10,3,0), t)

        self.assertEqual(datetime.datetime(2015,7,29, 10,3,0), sr_helpers.parse_sr_time_string('klockan 10:03', base_day))
        self.assertEqual(datetime.datetime(2015,7,28, 10,3,0), sr_helpers.parse_sr_time_string('Ig&#229;r klockan 10:03', base_day))
        self.assertEqual(datetime.datetime(2015,7,28, 10,3,0), sr_helpers.parse_sr_time_string('Ig&#229;r kl 10:03', base_day))
        self.assertEqual(datetime.datetime(2015,7,24, 10,3,0), sr_helpers.parse_sr_time_string('fredag 24 juli klockan 10:03', base_day))
        self.assertEqual(datetime.datetime(2015,7,24, 10,3,0), sr_helpers.parse_sr_time_string('m&#229;ndag 24 juli klockan 10:03', base_day))
        self.assertEqual(datetime.datetime(2015,7,24, 10,3,0), sr_helpers.parse_sr_time_string('söndag 24 juli klockan 10:03', base_day))
        self.assertEqual(datetime.datetime(2015,7,24, 10,3,0), sr_helpers.parse_sr_time_string('söndag 24 juli klockan 10:03', base_day))
    
        pass
    pass

if __name__ == '__main__':
    sys.exit(unittest.main(argv=['-v']))
    