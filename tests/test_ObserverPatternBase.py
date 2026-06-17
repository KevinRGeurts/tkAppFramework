"""
This module provides unit tests for:
    (1) Subject and (2) Observer classes
"""


# Standard imports
import unittest

# Local imports
from tkAppFramework.ObserverPatternBase import Subject, Observer, UpdateHint


class TestUpdateHint(UpdateHint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self._amount_to_add = kwargs.get('amount_to_add')


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

    def test_notify_with_hint(self):
        obs = Observer()
        sub = Subject()
        sub.attach(obs)
        x=0
        def f(hints):
            nonlocal x
            x+=hints[0]._amount_to_add
        obs.register_subject(sub, f)
        sub.notify([TestUpdateHint(amount_to_add=2)])
        self.assertEqual(2, x)

    def test_notify_with_hint_not_list(self):
        obs = Observer()
        sub = Subject()
        sub.attach(obs)
        x=0
        def f(hints):
            nonlocal x
            x+=hints[0]._amount_to_add
        obs.register_subject(sub, f)
        self.assertRaises(AssertionError, sub.notify, TestUpdateHint(amount_to_add=2))

    def test_notify_with_hint_UpdateHint(self):
        obs = Observer()
        sub = Subject()
        sub.attach(obs)
        x=0
        def f(hints):
            nonlocal x
            x+=hints[0]._amount_to_add
        obs.register_subject(sub, f)
        self.assertRaises(AssertionError, sub.notify, 'not an UpdateHint object')

    def test_attach_nonobserver(self):
        obs = Subject()
        sub = Subject()
        self.assertRaises(AssertionError, sub.attach, obs)

    def test_detach_missing_observer(self):
        obs = Observer()
        sub = Subject()
        try:
            sub.detach(obs)
        except ValueError as e:
            self.assertTrue(False)


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

    def test_update_with_hint(self):
        obs = Observer()
        sub = Subject()
        self.assertRaises(KeyError, obs.update, sub)
        x=0
        def f(hints):
            nonlocal x
            x+=hints[0]._amount_to_add     
        obs.register_subject(sub, f)
        obs.update(sub, [TestUpdateHint(amount_to_add=2)])
        self.assertEqual(2, x)

    def test_update_with_hint_not_list(self):
        obs = Observer()
        sub = Subject()
        self.assertRaises(KeyError, obs.update, sub)
        x=0
        def f(hints):
            nonlocal x
            x+=hints[0]._amount_to_add     
        obs.register_subject(sub, f)
        self.assertRaises(AssertionError, obs.update, sub, TestUpdateHint(amount_to_add=2))

    def test_update_with_hint_not_UpdateHint(self):
        obs = Observer()
        sub = Subject()
        self.assertRaises(KeyError, obs.update, sub)
        x=0
        def f(hints):
            nonlocal x
            x+=hints[0]._amount_to_add     
        obs.register_subject(sub, f)
        self.assertRaises(AssertionError, obs.update, sub, 'not an UpdateHint object')
        

if __name__ == '__main__':
    unittest.main()
