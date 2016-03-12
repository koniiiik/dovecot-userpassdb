Dovecot user-controllable passwords
===================================

Passwords used by your users to log into a system using SSH are precious.
Way too precious to have mail software store them in plaintext on
arbitrary devices (laptops, phones, ...). Unless you are using LDAP to
store password hashes for your system users, Dovecot doesn't offer an
out-of-the-box way to let regular users set passwords for IMAP that differ
from those they use to log into the system.

This tool provides a simple way of implementing separate passwords in
Dovecot for regular system users. Passwords are stored inside each user's
home directory, and they can be modified from the command line. It
implements Dovecot's checkpassword interface for password verification.

Future plans include:

* setting additional attributes (such as ``mail`` to override the
  system-default ``mail_location``)

Installation
------------

This is a regular Python package installable using ``pip``. Obviously, it
depends on Python (tested on 3.4+). If you're feeling adventurous, just
run ``pip install dovecot-userpassdb`` as root to have everything
installed inside ``/usr/local``. If you prefer to keep things tidy and
isolated, you can follow these steps instead:

#. Create a Python virtualenv::

    # python -m venv /usr/local/venv-dovecot-userpassdb
    # PIP="/usr/local/venv-dovecot-userpassdb/bin/pip"
    # $PIP install -U pip                                # to be up-to-date

#. Install the ``dovecot-userpassdb`` package inside the new virtualenv::

    # $PIP install dovecot-userpassdb

#. Make the newly-installed ``imap-passwd`` script available in system
   ``PATH``::

    # ln -s /usr/local/venv-dovecot-userpassdb/bin/imap-passwd /usr/local/bin

#. Finally, configure Dovecot to use the provided ``dovecot-checkpass``
   script, for example by including the following block::

    passdb {
        driver = checkpassword
        args = /usr/local/venv-dovecot-userpassdb/bin/dovecot-checkpass
    }
