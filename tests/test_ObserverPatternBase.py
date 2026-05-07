"""
This module provides unit tests for:
    (1) Subject and (2) Observer classes
"""


# Standard imports
import unittest

# Local imports
from tkAppFramework.ObserverPatternBase import Subject, Observer


class Test_Subject(unittest.TestCase):
    def test_attach_notify_detach(self):
        obs = Observer()
        sub = Subject()
        sub.attach(obs)
        x=0
        def f():
            nonlocal x
            x+=1
        obs.register_subject(sub, f)
        self.assertTrue(sub._observers.index(obs)>=0)
        sub.notify()
        self.assertEqual(1, x)
        sub.detach(obs)
        self.assertRaises(ValueError, sub._observers.index, obs)

    def test_attach_nonobserver(self):
        obs = Subject()
        sub = Subject()
        self.assertRaises(AssertionError, sub.attach, obs)

    def test_detach_missing_observer(self):
        obs = Observer()
        sub = Subject()
        self.assertRaises(ValueError, sub.detach, obs)


class Test_Observer(unittest.TestCase):
    def test_init(self):
        obs = Observer()
        self.assertEqual({}, obs._subjects)

    def test_register_subject(self):
        obs = Observer()
        sub = Subject()
        def f():
            pass
        obs.register_subject(sub, f)
        self.assertEqual(f, obs._subjects[sub])

    def test_register_subject_and_detach_from_subjects(self):
        obs = Observer()
        sub1 = Subject()
        sub1.attach(obs)
        sub2 = Subject()
        sub2.attach(obs)
        def f():
            pass
        obs.register_subject(sub1, f)
        obs.register_subject(sub2, f)
        self.assertEqual(f, obs._subjects[sub1])
        self.assertEqual(f, obs._subjects[sub2])
        obs._detach_from_subjects()
        self.assertEqual(0, len(sub1._observers))
        self.assertEqual(0, len(sub2._observers))
    
    def test_update(self):
        obs = Observer()
        sub = Subject()
        self.assertRaises(KeyError, obs.update, sub)
        x=0
        def f():
            nonlocal x
            x+=1     
        obs.register_subject(sub, f)
        obs.update(sub)
        self.assertEqual(1, x)
        

if __name__ == '__main__':
    unittest.main()
