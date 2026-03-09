"""
This module provides unit tests for the HelpModel class.
"""


# Standard imports
import unittest
import tempfile

# Local imports
from tkAppFramework.HelpModel import HelpModel


class Test_HelpModel(unittest.TestCase):
    def test_init_no_help_file(self):
        hm = HelpModel()
        self.assertEqual('', hm._help_file)
        self.assertEqual('txt', hm._help_format)
        self.assertEqual('', hm._txt_content)
        self.assertEqual('', hm._xhtml_content)
        self.assertEqual('', hm._md_content)

    def test_txt(self):
        help_content = 'Help file text content'
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as temp_file:
            temp_file.write(help_content)
            temp_file.close()
            hm = HelpModel(help_file=temp_file.name, help_format='txt')
            self.assertEqual(temp_file.name, hm._help_file)
            self.assertEqual('txt', hm._help_format)
            self.assertEqual(help_content, hm.get_help_content()[0])
            self.assertEqual('', hm._xhtml_content)
            self.assertEqual('', hm._md_content)

    def test_md(self):
        help_content = 'Help file markdown content'
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as temp_file:
            temp_file.write(help_content)
            temp_file.close()
            hm = HelpModel(help_file=temp_file.name, help_format='md')
            self.assertEqual(temp_file.name, hm._help_file)
            self.assertEqual('md', hm._help_format)
            self.assertEqual('', hm._txt_content)
            self.assertEqual('', hm._xhtml_content)
            self.assertEqual(help_content, hm._md_content)
            self.assertEqual('', hm.get_help_content()[0])

    def test_xhtml(self):
        help_content = 'Help file xhtml content'
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as temp_file:
            temp_file.write(help_content)
            temp_file.close()
            hm = HelpModel(help_file=temp_file.name, help_format='xhtml')
            self.assertEqual(temp_file.name, hm._help_file)
            self.assertEqual('xhtml', hm._help_format)
            self.assertEqual('', hm._txt_content)
            self.assertEqual(help_content, hm.get_help_content()[0])
            self.assertEqual('', hm._md_content)
 

if __name__ == '__main__':
    unittest.main()
