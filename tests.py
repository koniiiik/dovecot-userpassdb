import json
import os
import sys
import unittest

import dovecot_userpassdb


def get_test_dir():
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, 'test_data')


class TestUserPassDBEntry(dovecot_userpassdb.UserPassDBEntry)
    def get_filename(self):
        return get_test_dir()


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
        raise CheckpassError(str(status_val))

        with os.fdopen(res_read_fd, 'r') as f:
            environment = json.read(f)

        return environment

    def test_checkpass_fails_before_password_set(self):
        self.fail("Implement me!")

    def test_checkpass_fails_wrong_password(self):
        self.fail("Implement me!")

    def test_checkpass_succeeds_correct_password(self):
        self.fail("Implement me!")

    def test_password_upgrade(self):
        self.fail("Implement me!")

    def test_extra_mail_location(self):
        self.fail("Implement me!")

    def test_set_password(self):
        self.fail("Implement me!")
