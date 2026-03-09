"""
This module provides unit tests for the XHTMLParserForTkTextWidget class.
"""


# Standard imports
import unittest

# Local imports
from tkAppFramework.xhtml_parser_for_tktextwidget import XHTMLParserForTkTextWidget


class Test_XHTMLParserForTkTextWidget(unittest.TestCase):
    def test_init_populate_tag_map(self):
        parser = XHTMLParserForTkTextWidget()
        self.assertEqual(1, len(parser._tag_map))
        exp_val = ('tag_h1', {'foreground':'red'})
        act_val = parser._tag_map['h1']
        self.assertEqual(exp_val, act_val)

    def test_xhtml_string_to_elements(self):
        parser = XHTMLParserForTkTextWidget()
        act_val = parser.xhtml_string_to_elements('<h1>This is a Heading Level 1</h1>')
        # TODO: When this is working, the expected text in the second list should not have the html tags
        exp_val = ([('tag_h1', {'foreground':'red'})], [('tag_h1', '<h1>This is a Heading Level 1</h1>')])
        self.assertEqual(exp_val, act_val)




if __name__ == '__main__':
    unittest.main()
