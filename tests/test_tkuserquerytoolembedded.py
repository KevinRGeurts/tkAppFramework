"""
This module provides unit tests for the tkUserQueryToolEmbedded class and subclasses.
"""


# Standard
import unittest
import tkinter as tk

# Local
from tkAppFramework.tkUserQueryToolEmbedded import tkMenuUserUserQuerytToolEmbedded, tkUserQueryToolEmbedded
import UserResponseCollector.UserQueryCommand
import UserResponseCollector.UserQueryReceiver


class tkDummyUserQueryToolEmbedded(tkUserQueryToolEmbedded):
    def __init__(self, parent):
        super().__init__(parent, tool_name='Dummy', query_type=UserResponseCollector.UserQueryCommand.UserQueryCommand)
        self._response = 'A response'

    def _CreateWidgets(self):
        # Do nothing, but also do not raise NotImplementedError
        return None


class Test_tkUserQueryToolEmbedded(unittest.TestCase):
    def test_init(self):
        root = tk.Tk()
        self.assertRaises(AssertionError, tkUserQueryToolEmbedded, root, tool_name={}) # tool_name is NOT a str
        self.assertRaises(AssertionError, tkUserQueryToolEmbedded, root, tool_name='') # tool_name is 0-length
        self.assertRaises(AssertionError, tkUserQueryToolEmbedded, root, query_type={}) # query_type is NOT a UserResponseCollector.UserQueryCommand
        self.assertRaises(NotImplementedError, tkUserQueryToolEmbedded, root, query_type=UserResponseCollector.UserQueryCommand.UserQueryCommandNumberFloat) # _CreateWidgets() method not implemented


class Test_tkDummyUserQueryToolEmbedded(unittest.TestCase):
    def test_property_tool_name(self):
        root = tk.Tk()
        tool_wid = tkDummyUserQueryToolEmbedded(root)
        exp_val = 'Dummy'
        act_val = tool_wid.tool_name
        self.assertEqual(act_val, exp_val)

    def test_property_query_type(self):
        root = tk.Tk()
        tool_wid = tkDummyUserQueryToolEmbedded(root)
        exp_val = UserResponseCollector.UserQueryCommand.UserQueryCommand
        act_val = tool_wid.query_type
        self.assertEqual(act_val, exp_val)

    def test_property_response(self):
        root = tk.Tk()
        tool_wid = tkDummyUserQueryToolEmbedded(root)
        exp_val = 'A response'
        act_val = tool_wid.response
        self.assertEqual(act_val, exp_val)

    def test_response_setter(self):
        root = tk.Tk()
        tool_wid = tkDummyUserQueryToolEmbedded(root)
        exp_val = 'Another response'
        tool_wid.response = exp_val
        act_val = tool_wid.response
        self.assertEqual(act_val, exp_val)
     
    def test_disable(self):
        root = tk.Tk()
        tool_wid = tkDummyUserQueryToolEmbedded(root)
        self.assertRaises(NotImplementedError, tool_wid.disable)
        
    def test_setup_query(self):
        root = tk.Tk()
        tool_wid = tkDummyUserQueryToolEmbedded(root)
        extra={'query_dic':{'1':'Option 1'}}
        tool_wid.setup_query(extra) # Does not assert
        self.assertRaises(AssertionError, tool_wid.setup_query, []) # extra is NOT a dict (here it is a listcd)


class Test_tkMenuUserUserQuerytToolEmbedded(unittest.TestCase):
    def test_property_tool_name(self):
        root = tk.Tk()
        tool_wid = tkMenuUserUserQuerytToolEmbedded(root)
        exp_val = 'Menu'
        act_val = tool_wid.tool_name
        self.assertEqual(act_val, exp_val)

    def test_property_query_type(self):
        root = tk.Tk()
        tool_wid = tkMenuUserUserQuerytToolEmbedded(root)
        exp_val = UserResponseCollector.UserQueryCommand.UserQueryCommandMenu
        act_val = tool_wid.query_type
        self.assertEqual(act_val, exp_val)

    def test_property_response(self):
        root = tk.Tk()
        tool_wid = tkMenuUserUserQuerytToolEmbedded(root)
        exp_val = ''
        act_val = tool_wid.response
        self.assertEqual(act_val, exp_val) 
        
    def test_setup_query(self):
        root = tk.Tk()
        tool_wid = tkMenuUserUserQuerytToolEmbedded(root)
        extra={'query_dic':{'1':'Option 1'}}
        tool_wid.setup_query(extra)
        exp_val = len(extra)
        act_val = len(tool_wid._choices)
        self.assertEqual(act_val, exp_val)

    def test_setup_query_bad(self):
        root = tk.Tk()
        tool_wid = tkMenuUserUserQuerytToolEmbedded(root)
        extra={'not_query_dic':{'1':'Option 1'}}
        self.assertRaises(KeyError, tool_wid.setup_query, extra)
        
    def test_onSelectChoice(self):
        root = tk.Tk()
        tool_wid = tkMenuUserUserQuerytToolEmbedded(root)
        extra={'query_dic':{'1':'Option 1','2':'Option 2'}}
        tool_wid.setup_query(extra)
        exp_val = '2'
        tool_wid.onSelectChoice(exp_val)
        act_val = tool_wid.response
        self.assertEqual(act_val, exp_val)


if __name__ == '__main__':
    unittest.main()
