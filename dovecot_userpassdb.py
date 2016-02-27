import getpass
import hashlib
import hmac
import json
import os
import pwd
import sys
import traceback

from passlib.context import CryptContext


FILENAME_TEMPLATE = '{homedir}/.config/imaprc.json'
ENCODING = 'utf-8'
crypt_context = CryptContext(
    schemes=('pbkdf2_sha512', 'bcrypt', 'sha512_crypt'),
    default='pbkdf2_sha512',
)
EMPTY_PWHASH = crypt_context.encrypt('')


class UserPassDBEntry(object):
    """Represents one user's Dovecot settings.
    """
    def __init__(self, username):
        self.loaded_file = False
        self.need_update = False
        self.pw_hash = None

        try:
            self.pwd = pwd.getpwnam(username)
        except KeyError:
            self.pwd = pwd.getpwnam('nobody')

        self.homedir = self.pwd.pw_dir
        self.filename = self.get_filename()
        self.read_imaprc()

    def get_filename(self):
        """Hook to customize the filesystem path to the settings file.

        Intended to simplify testing. Can assume the presence of
        attributes pwd, homedir.
        """
        return FILENAME_TEMPLATE.format(homedir=self.homedir)

    def read_imaprc(self):
        # TODO: lock the file?
        try:
            with open(self.filename) as f:
                attrs = json.load(f)
        except IOError:
            return
        self.loaded_file = True
        self.pw_hash = attrs.get('password', self.pw_hash)

    def write_imaprc(self):
        # TODO: lock the file?
        state = {
            'password': self.pw_hash,
        }
        try:
            with open(self.filename, 'w') as f:
                json.dump(state, f)
        except IOError:
            # TODO
            raise

    def verify_password(self, password):
        valid, new_hash = crypt_context.verify_and_update(
            password, self.pw_hash or EMPTY_PWHASH
        )

        if not self.pw_hash:
            return False

        # TODO: update stuff...?
        return valid

    def set_password(self, new_password):
        self.pw_hash = crypt_context.encrypt(new_password)
        self.need_update = True
        # TODO: write here?

    def get_dovecot_environ(self):
        return {
            'USER': self.pwd.pw_name,
            'HOME': self.homedir,
            'userdb_uid': str(self.pwd.pw_uid),
            'userdb_gid': str(self.pwd.pw_gid),
            'EXTRA': 'userdb_uid userdb_gid',
        }

    @classmethod
    def checkpass(cls, argv):
        """Implementation of the checkpassword protocol.
        """
        with os.fdopen(3) as infile:
            data = infile.read(512).split('\0')
        username, password = data[:2]

        db_entry = cls(username)

        if not db_entry.verify_password(password):
            return 1

        os.environ.update(db_entry.get_dovecot_environ())
        os.execvp(argv[1], argv[1:])

    @classmethod
    def checkpass_main(cls, argv=sys.argv):
        """Main entry point for checkpassword. Wraps checkpass for error
        handling.
        """
        try:
            return cls.checkpass(argv) or 111
        except Exception:
            # TODO: proper logging?
            traceback.print_exc(file=sys.stderr)
            return 111

    @classmethod
    def set_and_write_password(cls, username, password):
        db_entry = cls(username)
        db_entry.set_password(password)
        db_entry.write_imaprc()

    @classmethod
    def change_password(cls):
        """Entry point for password change.
        """
        current_user = getpass.getuser()
        new_pass1 = getpass.getpass("New IMAP password: ")
        new_pass2 = getpass.getpass("New IMAP password (again): ")

        if new_pass1 != new_pass2:
            raise ValueError("Provided passwords do not match.")

        cls.set_and_write_password(current_user, new_pass1)
