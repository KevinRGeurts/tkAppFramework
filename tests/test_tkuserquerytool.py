"""
This module provides unit tests for the tkUserQueryToolModal class and subclasses.
"""


# Standard
import unittest

# Local
from tkAppFramework.tkUserQueryToolModal import tkUserQueryToolModal, tkPathSaveToolModal, tkPathOpenToolModal
import UserResponseCollector.UserQueryCommand
import UserResponseCollector.UserQueryReceiver


class Test_tkUserQueryToolModal(unittest.TestCase):
    def test_init_prop_gets(self):
        tool = tkUserQueryToolModal(tool_name='Test Tool', query_type=UserResponseCollector.UserQueryCommand.UserQueryCommand)
        self.assertEqual(tool.tool_name, 'Test Tool')
        self.assertEqual(tool.query_type, UserResponseCollector.UserQueryCommand.UserQueryCommand)

    def test_run(self):
        tool = tkUserQueryToolModal(tool_name='Test Tool', query_type=UserResponseCollector.UserQueryCommand.UserQueryCommand)
        reponse = tool.run()
        self.assertEqual(reponse, '')


class Test_tkPathSaveToolModal(unittest.TestCase):
    def test_init_prop_gets(self):
        tool = tkPathSaveToolModal()
        self.assertEqual(tool.tool_name, 'File Save Path...')
        self.assertEqual(tool.query_type, UserResponseCollector.UserQueryCommand.UserQueryCommandPathSave)


class Test_tkPathOpenToolModal(unittest.TestCase):
    def test_init_prop_gets(self):
        tool = tkPathOpenToolModal()
        self.assertEqual(tool.tool_name, 'File Open Path...')
        self.assertEqual(tool.query_type, UserResponseCollector.UserQueryCommand.UserQueryCommandPathOpen)


if __name__ == '__main__':
    unittest.main()
