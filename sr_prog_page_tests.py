import unittest
import lxml.etree as ET
import lxml.html as EHTML

import common
from common import is_none_or_empty

from XmlHandler import get_namespace

from sr_prog_page import SrProgramPageParser

div___episode_list__item__title =  ET.fromstring("""
        <div class="episode-list__item__title">
                                                    
            <a href="/sida/avsnitt/1024121?programid=4426" data-clickable-content="link" class="heading heading--small">Fort gick det inte!</a>
            <span class="tiny-text"><span class="date"><abbr title="Onsdag 14 februari klockan 17:06">Ons 14 feb kl 17:06</abbr></span>
                <span class="duration"><abbr title="114 minuter">(114 min)</abbr></span>
            </span>
            <div class="episode-list__item__description episode-list__item__description--show-large">
                                                        
                <p class="text__block text--small">
                                                            
                    Idag hörs musik av en man som verkligen inte hade bråttom, Joseph Canteloubes sånger lånar toner av hemtraktens folkmusik i Frankrike.
                </p>
            </div>
        </div>
""")

class Test_sr_prog_page_tests(unittest.TestCase):
    def test_parse_find_a__data_clickable_content(self):
        el_ls = SrProgramPageParser.parse_find_a__data_clickable_content(div___episode_list__item__title)
        self.assertIsNotNone(el_ls)

if __name__ == '__main__':
    unittest.main(argv=['test'])
