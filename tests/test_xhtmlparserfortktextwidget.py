"""
This module provides unit tests for the XHTMLParserForTkTextWidget class.
"""


# Standard imports
import unittest
import logging

# Local imports
from tkAppFramework.xhtml_parser_for_tktextwidget import XHTMLParserForTkTextWidget, TkWidgetXHTMLParserInterface
from tkAppFramework.exceptions import NoWidgetTagConfigurationAvailableForXHTMLTag


class TextWidgetTestMock(TkWidgetXHTMLParserInterface):
    """
    Class serves as a mock-up of a tkinter Text widget, for testing XHTMLParserForTkTextWidget class.
    It extends required methods defined by TkWidgetXHTMLParserInterface class and stores some parameter values
    from the method calls to be used in assertEqual(...) tests.
    """
    def __init__(self):
        super().__init__()
        # List contains tuples (starting_index, ending_index, inserted_text), as (string, string, string)
        self._inserted_text=[]
        self._text_length=0
        # List contains tuples (starting_index, ending_index, tagName, as (string, string, string)
        self._added_tags=[]
        # List contains tuples (tagName, options_dict), as (string, dict)
        self._configed_tags=[]
        # List contains tuples (tagName, bound_link_url), as (string, string)
        self._bound_tags=[]

    def insert_text(self, starting_index='', text=''):
        """
        Method used by XHTML parser to insert text into Text widget.
        :parameter start_index: tkinter Text widget index to start any text insertions, as string
        :parameter text: The text to insert into the Text widget, as string
        :return: tkinter Text widget index at the end of any text insertions, as string
        """
        super().insert_text(starting_index, text)
        self._text_length += len(text)
        ending_index = self._text_length
        self._inserted_text.append((str(starting_index), str(ending_index), text))
        return str(ending_index)

    def tag_text(self, starting_index='', ending_index='', tagName='', link_url=''):
        """
        Method used by XHTML parser to tag text in a Text widget.
        :parameter start_index: tkinter Text widget index of start of text to tag, as string
        :parameter ending_index: tkinter Text widget index of the end of any text to tag, as string
        :parameter tagName: The tagName with which to tag the text, as string
        :parameter link_url: The URL to "bind" to tagName, as string
        :return: None
        """
        super().tag_text(starting_index, ending_index, tagName)
        self._added_tags.append((starting_index, ending_index, tagName))
        if len(link_url) > 0:
            self._bound_tags.append((tagName, link_url))
        return None

    def config_tag(self, tagName='', options_dict={}):
        """
        Method used by XHTML parser to add and configure options for a tag in tkinter Text widget.
        :parameter tagName: The tagName with which to tag the text, as string
        :parameter options_dict: The dictionary of configuration options for the tag, as dict with key = option_name, value = option_setting
        :return: None
        """
        super().config_tag(tagName, options_dict)
        self._configed_tags.append((tagName, options_dict))
        return None

    def get_start_index(self):
        """
        Call back method used by XHTML parser to get the current insertion index for the tkinter Text widget.
        :return: The current index, as string
        """
        super().get_start_index()
        index = self._text_length
        return str(index)


class Test_XHTMLParserForTkTextWidget(unittest.TestCase):
    def test_init_populate_tag_map(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
        self.assertEqual(9, len(parser._tag_map))
        exp_val = 'tag_h1'
        act_val = parser._tag_map['h1'][0]
        self.assertEqual(exp_val, act_val)
        self.assertEqual(0, len(mock._configed_tags))
        
    def test_getTagIdSuffix(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
        self.assertEqual('0', parser._getTagIdSuffix())
        self.assertEqual('1', parser._getTagIdSuffix())

    def test_build_tagName(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
        self.assertEqual('tag_h1_0', parser.build_tagName('h1')[0])
        self.assertEqual('tag_em_1', parser.build_tagName('em')[0])
        act_val = parser.build_tagName('h1')
        self.assertEqual('tag_h1_2', act_val[0])
        self.assertEqual(18.0, act_val[1]['spacing3'])

    def test_build_tagName_fail(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
        self.assertRaises(NoWidgetTagConfigurationAvailableForXHTMLTag, parser.build_tagName, 'unconfigured_xhtml_tag')

    def test_process_xhtml_1_element(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
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
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
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
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
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
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
        parser.process_xhtml('<body><h1>Heading</h1><p><em>emphasized text</em></p></body>')
        # Check text insertions
        act_val = mock._inserted_text
        exp_val = [('0', '7', 'Heading'), ('7', '22', 'emphasized text')]
        self.assertListEqual(exp_val, act_val)
        # Check added tags
        act_val = mock._added_tags
        exp_val = [('0', '0 +22c', 'tag_body_0'), ('0', '0 +7c', 'tag_h1_1'), ( '7', '7 +15c','tag_p_2'), ('7', '7 +15c', 'tag_em_3')]
        self.assertListEqual(exp_val, act_val)

    def test_process_xhtml_unordered_list(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
        parser.process_xhtml('<body><h2>Unordered list</h2><ul><li>Item 1</li><li>Item 2</li></ul></body>')
        # Check text insertions
        act_val = mock._inserted_text
        exp_val = [('0', '14', 'Unordered list'), ('14', '22', '* Item 1'), ('22', '30', '* Item 2')]
        self.assertListEqual(exp_val, act_val)
        # Check added tags
        act_val = mock._added_tags
        exp_val = [('0', '0 +30c', 'tag_body_0'), ('0', '0 +14c', 'tag_h2_1'), ( '14', '14 +8c','tag_li_2'), ('22', '22 +8c', 'tag_li_3')]
        self.assertListEqual(exp_val, act_val)

    def test_process_xhtml_ordered_list(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
        parser.process_xhtml('<body><h2>Ordered list</h2><ol><li>Item 1</li><li>Item 2</li></ol></body>')
        # Check text insertions
        act_val = mock._inserted_text
        exp_val = [('0', '12', 'Ordered list'), ('12', '22', '(1) Item 1'), ('22', '32', '(2) Item 2')]
        self.assertListEqual(exp_val, act_val)
        # Check added tags
        act_val = mock._added_tags
        exp_val = [('0', '0 +32c', 'tag_body_0'), ('0', '0 +12c', 'tag_h2_1'), ( '12', '12 +10c','tag_li_2'), ('22', '22 +10c', 'tag_li_3')]
        self.assertListEqual(exp_val, act_val)

    def test_process_xhtml_code_block(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
        parser.process_xhtml('<body>Regular <code>code block</code> regular</body>')
        # Check text insertions
        act_val = mock._inserted_text
        exp_val = [('0', '8', 'Regular '), ('8', '18', 'code block'), ('18', '26', ' regular')]
        self.assertListEqual(exp_val, act_val)
        # Check added tags
        act_val = mock._added_tags
        exp_val = [('0', '0 +26c', 'tag_body_0'), ('8', '8 +10c', 'tag_code_1')]
        self.assertListEqual(exp_val, act_val)

    def test_process_xhtml_heading_3(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
        parser.process_xhtml('<body><h3>Heading level 3</h3></body>')
        # Check text insertions
        act_val = mock._inserted_text
        exp_val = [('0', '15', 'Heading level 3')]
        self.assertListEqual(exp_val, act_val)
        # Check added tags
        act_val = mock._added_tags
        exp_val = [('0', '0 +15c', 'tag_body_0'), ('0', '0 +15c', 'tag_h3_1')]
        self.assertListEqual(exp_val, act_val)

    def test_process_xhtml_anchor(self):
        mock = TextWidgetTestMock()
        parser = XHTMLParserForTkTextWidget(mock, logging.INFO)
        parser.process_xhtml('<body><a href="https://github.com/KevinRGeurts/tkAppFramework">GitHub</a></body>')
        # Check text insertions
        act_val = mock._inserted_text
        exp_val = [('0', '6', 'GitHub')]
        self.assertListEqual(exp_val, act_val)
        # Check added tags
        act_val = mock._added_tags
        exp_val = [('0', '0 +6c', 'tag_body_0'), ('0', '0 +6c', 'tag_a_1')]
        self.assertListEqual(exp_val, act_val)
        # Check added bindings
        act_val = mock._bound_tags
        exp_val = [('tag_a_1', 'https://github.com/KevinRGeurts/tkAppFramework')]
        self.assertListEqual(exp_val, act_val)
        

if __name__ == '__main__':
    unittest.main()
