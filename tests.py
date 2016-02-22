import multiprocessing
import os
import unittest

import dovecot_userpassdb


def get_test_dir():
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, 'test_data')


class TestUserPassDBEntry(dovecot_userpassdb.UserPassDBEntry)
    def get_filename(self):
        return get_test_dir()


class DovecotUserPassDBTestCase(unittest.TestCase):
    def setUp(self):
        os.mkdir(get_test_dir())

    def tearDown(self):
        shutil.rmtree(get_test_dir())

    def run_checkpass(self):
        self.fail("Implement me!")
        proc = None
        return proc.exitcode

    def test_checkpass_fails_before_password_set(self):
        self.fail("Implement me!")

    def test_checkpass_fails_wrong_password(self):
        self.fail("Implement me!")

    def test_checkpass_succeeds_correct_password(self):
        self.fail("Implement me!")

    def test_extra_mail_location(self):
        self.fail("Implement me!")

    def test_set_password(self):
        self.fail("Implement me!")
