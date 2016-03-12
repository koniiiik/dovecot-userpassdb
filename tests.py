import json
import os
import pwd
import shutil
import sys
import time
import unittest

import dovecot_userpassdb


def get_test_dir():
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, 'test_data')
get_test_dir.__test__ = False


def get_test_filename():
    return os.path.join(get_test_dir(), 'imaprc.json')
get_test_filename.__test__ = False


class TestUserPassDBEntry(dovecot_userpassdb.UserPassDBEntry):
    def get_filename(self):
        return get_test_filename()


class CheckpassError(Exception):
    """Exception raised by run_checkpass when it returns a non-zero code.
    """
    pass


class DovecotUserPassDBTestCase(unittest.TestCase):
    def setUp(self):
        os.mkdir(get_test_dir())

    def tearDown(self):
        shutil.rmtree(get_test_dir())

    def run_checkpass(self, username, password):
        """Run checkpass in a subprocess, and return its result.

        Calls the checkpass main function in a subprocess, sends it a
        username, and a password, and instructs it to run ./dump_env.py on
        success, which dumps its os.environ as a JSON dict into FD 4.

        Returns the environment dict.
        """
        pass_read_fd, pass_write_fd = os.pipe()
        res_read_fd, res_write_fd = os.pipe()
        os.set_inheritable(pass_read_fd, True)
        os.set_inheritable(res_write_fd, True)

        child_pid = os.fork()
        if child_pid == 0:
            # Child process.
            os.close(pass_write_fd)
            os.close(res_read_fd)
            os.dup2(pass_read_fd, 3)
            os.dup2(res_write_fd, 4)
            argv = [sys.argv[0], "./dump_env.py"]
            # We need to skip the unittest error handlers here.
            os._exit(TestUserPassDBEntry.checkpass_main(argv=argv))

        # Parent process.
        os.close(pass_read_fd)
        os.close(res_write_fd)

        with os.fdopen(pass_write_fd, 'w') as f:
            f.write('\0'.join([username, password, '']))

        pid, status = os.waitpid(child_pid, 0)

        signal = status & 0xff
        status_val = (status & (0xff << 8)) >> 8
        self.assertEqual(signal, 0, "Child killed by signal {}.".format(signal))
        if status_val:
            raise CheckpassError(str(status_val))

        with os.fdopen(res_read_fd, 'r') as f:
            environment = json.load(f)

        return environment

    def test_checkpass_fails_before_password_set(self):
        with self.assertRaisesRegex(CheckpassError, '^1$'):
            self.run_checkpass('user', '')

        with self.assertRaisesRegex(CheckpassError, '^1$'):
            self.run_checkpass('user', 'password')

    def test_set_new_password(self):
        TestUserPassDBEntry.set_and_write_password('user', 'password123')
        with open(get_test_filename(), 'r') as f:
            imaprc_state = json.load(f)

        self.assertIn('password', imaprc_state)
        self.assertTrue(dovecot_userpassdb.crypt_context.verify(
            'password123', imaprc_state['password']
        ))

    def test_change_password(self):
        TestUserPassDBEntry.set_and_write_password('user', 'password123')

        with open(get_test_filename(), 'r') as f:
            imaprc_state = json.load(f)

        self.assertIn('password', imaprc_state)

        TestUserPassDBEntry.set_and_write_password('user', 'password456')
        with open(get_test_filename(), 'r') as f:
            imaprc_state = json.load(f)

        self.assertIn('password', imaprc_state)
        self.assertTrue(dovecot_userpassdb.crypt_context.verify(
            'password456', imaprc_state['password']
        ))

    def test_checkpass_fails_wrong_password(self):
        TestUserPassDBEntry.set_and_write_password('user', 'password123')

        with self.assertRaisesRegex(CheckpassError, '^1$'):
            self.run_checkpass('user', 'wrong password')

    def test_checkpass_succeeds_correct_password(self):
        TestUserPassDBEntry.set_and_write_password('nobody', 'password123')
        env = self.run_checkpass('nobody', 'password123')
        self.assertEqual(env['EXTRA'], 'userdb_uid userdb_gid')

        nobody_pwd = pwd.getpwnam('nobody')
        self.assertEqual(env['USER'], 'nobody')
        self.assertEqual(env['HOME'], nobody_pwd.pw_dir)
        self.assertEqual(env['userdb_uid'], str(nobody_pwd.pw_uid))
        self.assertEqual(env['userdb_gid'], str(nobody_pwd.pw_gid))

    def test_timing_without_configured_password(self):
        TestUserPassDBEntry.set_and_write_password('nobody', 'password123')

        # Just to see that it's correct.
        self.run_checkpass('nobody', 'password123')

        # To reduce the impact of outliers.
        checkpass_rounds = 5

        # We need monotonic() here, not clock(), because the actual CPU
        # time is spent in subprocesses.
        start = time.monotonic()
        for i in range(checkpass_rounds):
            with self.assertRaisesRegex(CheckpassError, '^1$'):
                self.run_checkpass('nobody', 'password456')
        end = time.monotonic()
        successful_time = end - start

        os.unlink(get_test_filename())

        start = time.monotonic()
        for i in range(checkpass_rounds):
            with self.assertRaisesRegex(CheckpassError, '^1$'):
                self.run_checkpass('nobody', 'password123')
        end = time.monotonic()
        unsuccessful_time = end - start

        delta = 0.2 * max(successful_time, unsuccessful_time)
        self.assertAlmostEqual(successful_time, unsuccessful_time, delta=delta)

    @unittest.skip("TODO")
    def test_password_upgrade(self):
        self.fail("Implement me!")

    @unittest.skip("TODO")
    def test_extra_mail_location(self):
        self.fail("Implement me!")
