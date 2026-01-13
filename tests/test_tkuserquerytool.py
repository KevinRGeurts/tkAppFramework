"""
This module provides unit tests for the tkUserQueryTool class and subclasses.
"""


# Standard
import unittest

# Local
from tkAppFramework.tkUserQueryTool import tkUserQueryTool, tkPathSaveTool, tkPathOpenTool
import UserResponseCollector.UserQueryCommand
import UserResponseCollector.UserQueryReceiver


class Test_tkUserQueryTool(unittest.TestCase):
    def test_init_prop_gets(self):
        tool = tkUserQueryTool(tool_name='Test Tool', query_type=UserResponseCollector.UserQueryCommand.UserQueryCommand)
        self.assertEqual(tool.tool_name, 'Test Tool')
        self.assertEqual(tool.query_type, UserResponseCollector.UserQueryCommand.UserQueryCommand)

    def test_run(self):
        tool = tkUserQueryTool(tool_name='Test Tool', query_type=UserResponseCollector.UserQueryCommand.UserQueryCommand)
        reponse = tool.run()
        self.assertEqual(reponse, '')


class Test_tkPathSaveTool(unittest.TestCase):
    def test_init_prop_gets(self):
        tool = tkPathSaveTool()
        self.assertEqual(tool.tool_name, 'File Save Path...')
        self.assertEqual(tool.query_type, UserResponseCollector.UserQueryCommand.UserQueryCommandPathSave)


class Test_tkPathOpenTool(unittest.TestCase):
    def test_init_prop_gets(self):
        tool = tkPathOpenTool()
        self.assertEqual(tool.tool_name, 'File Open Path...')
        self.assertEqual(tool.query_type, UserResponseCollector.UserQueryCommand.UserQueryCommandPathOpen)


if __name__ == '__main__':
    unittest.main()
