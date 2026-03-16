"""
This module provides unit tests for the XHTMLParserForTkTextWidget class.
"""


# Standard imports
import unittest
import logging
from tkinter.font import Font

# Local imports
from tkAppFramework.xhtml_parser_for_tktextwidget import XHTMLParserForTkTextWidget
from tkAppFramework.exceptions import NoWidgetTagConfigurationAvailableForXHTMLTag


class TextWidgetTestMock:
    """
    Class serves as a mock-up of a tkinter Text widget, for testing XHTMLParserForTkTextWidget class.
    It provides required call back functions and stores some parameter values from the call back functions
    to be used in assertEqual(...) tests.
    """
    def __init__(self):
        # List contains tuples (starting_index, ending_index, inserted_text), as (string, string, string)
        self._inserted_text=[]
        self._text_length=0
        # List contains tuples (starting_index, ending_index, tagName, as (string, string, string)
        self._added_tags=[]
        #List contains tuples (tagName, options_dict), as (string, dict)
        self._configed_tags=[]

    def _insert_text(self, starting_index='', text=''):
        """
        Call back method used by XHTML parser to insert text into Text widget.
        :parameter start_index: tkinter Text widget index to start any text insertions, as string
        :parameter text: The text to insert into the Text widget, as string
        :return: tkinter Text widget index at the end of any text insertions, as string
        """
        assert(type(starting_index)==str)
        assert(type(text)==str)
        self._text_length += len(text)
        ending_index = self._text_length
        self._inserted_text.append((str(starting_index), str(ending_index), text))
        return str(ending_index)

    def _tag_text(self, starting_index='', ending_index='', tagName=''):
        """
        Call back method used by XHTML parser to tag text in a Text widget.
        :parameter start_index: tkinter Text widget index of start of text to tag, as string
        :parameter ending_index: tkinter Text widget index of the end of any text to tag, as string
        :parameter tagName: The tagName with which to tag the text, as string
        :return: None
        """
        assert(type(starting_index)==str)
        assert(type(ending_index)==str)
        assert(type(tagName)==str)
        self._added_tags.append((starting_index, ending_index, tagName))
        return None

    def _config_tag(self, tagName='', options_dict={}):
        """
        Call back method used by XHTML parser to add and configure options for a tag in tkinter Text widget.
        :parameter tagName: The tagName with which to tag the text, as string
        :parameter options_dict: The dictionary of configuration options for the tag, as dict with key = option_name, value = option_setting
        :return: None
        """
        assert(type(tagName)==str)
        assert(type(options_dict)==dict)
        self._configed_tags.append((tagName, options_dict))
        return None

    def _get_start_index(self):
        """
        Call back method used by XHTML parser to get the current insertion index for the tkinter Text widget.
        :return: The current index, as string
        """
        index = self._text_length
        return str(index)


class Test_XHTMLParserForTkTextWidget(unittest.TestCase):
    def test_init_populate_tag_map(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock._insert_text, mock._tag_text, mock._config_tag, mock._get_start_index, logging.DEBUG)
        self.assertEqual(7, len(parser._tag_map))
        exp_val = 'tag_h1'
        act_val = parser._tag_map['h1'][0]
        self.assertEqual(exp_val, act_val)
        self.assertEqual(0, len(mock._configed_tags))
        
    def test_getTagIdSuffix(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock._insert_text, mock._tag_text, mock._config_tag, mock._get_start_index, logging.DEBUG)
        self.assertEqual('0', parser._getTagIdSuffix())
        self.assertEqual('1', parser._getTagIdSuffix())

    def test_build_tagName(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock._insert_text, mock._tag_text, mock._config_tag, mock._get_start_index, logging.DEBUG)
        self.assertEqual('tag_h1_0', parser.build_tagName('h1')[0])
        self.assertEqual('tag_em_1', parser.build_tagName('em')[0])
        act_val = parser.build_tagName('h1')
        self.assertEqual('tag_h1_2', act_val[0])
        exp_font = Font(family='Helvetica', size=20, weight='bold')
        self.assertEqual(18.5, act_val[1]['spacing3'])

    def test_build_tagName_fail(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock._insert_text, mock._tag_text, mock._config_tag, mock._get_start_index, logging.DEBUG)
        self.assertRaises(NoWidgetTagConfigurationAvailableForXHTMLTag, parser.build_tagName, 'unconfigured_xhtml_tag')

    def test_process_xhtml_1_element(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock._insert_text, mock._tag_text, mock._config_tag, mock._get_start_index, logging.DEBUG)
        parser.process_xhtml('<h1>This is a Heading Level 1</h1>')
        # Check text insertion
        act_val = mock._inserted_text
        exp_val = [('0', '25', 'This is a Heading Level 1')]
        self.assertListEqual(exp_val, act_val)
        # Check added tags
        act_val = mock._added_tags
        exp_val = [('0', '0 +25c', 'tag_h1_0')]
        self.assertListEqual(exp_val, act_val)

    def test_process_xhtml_2_nested_elements_middle(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock._insert_text, mock._tag_text, mock._config_tag, mock._get_start_index, logging.DEBUG)
        parser.process_xhtml('<h1>This is a <em>Heading</em> Level 1</h1>')
        # Check text insertions
        act_val = mock._inserted_text
        exp_val = [('0', '10', 'This is a '), ('10', '17', 'Heading'), ('17', '25', ' Level 1')]
        self.assertListEqual(exp_val, act_val)
        # Check added tags
        act_val = mock._added_tags
        exp_val = [('0', '0 +25c', 'tag_h1_0'), ('10', '10 +7c', 'tag_em_1')]
        self.assertListEqual(exp_val, act_val)
        
    def test_process_xhtml_2_nested_elements_end(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock._insert_text, mock._tag_text, mock._config_tag, mock._get_start_index, logging.DEBUG)
        parser.process_xhtml('<h1>This is a Heading Level <em>1</em></h1>')
        # Check text insertions
        act_val = mock._inserted_text
        exp_val = [('0', '24', 'This is a Heading Level '), ('24', '25', '1')]
        self.assertListEqual(exp_val, act_val)
        # Check added tags
        act_val = mock._added_tags
        exp_val = [('0', '0 +25c', 'tag_h1_0'), ('24', '24 +1c', 'tag_em_1')]
        self.assertListEqual(exp_val, act_val)

    def test_process_xhtml_2_serial_elements(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock._insert_text, mock._tag_text, mock._config_tag, mock._get_start_index, logging.DEBUG)
        parser.process_xhtml('<body><h1>Heading</h1><p><em>emphasized text</em></p></body>')
        # Check text insertions
        act_val = mock._inserted_text
        exp_val = [('0', '7', 'Heading'), ('7', '22', 'emphasized text')]
        self.assertListEqual(exp_val, act_val)
        # Check added tags
        act_val = mock._added_tags
        exp_val = [('0', '0 +22c', 'tag_body_0'), ('0', '0 +7c', 'tag_h1_1'), ( '7', '7 +15c','tag_p_2'), ('7', '7 +15c', 'tag_em_3')]
        self.assertListEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
