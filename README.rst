Dovecot user-controllable passwords
===================================

This tool provides a simple way of implementing separate passwords in
Dovecot for regular system users. Passwords are stored inside each user's
home directory, and they can be modified from the command line. It
implements Dovecot's checkpassword interface for password verification.

Future plans include:

* setting additional attributes (such as ``mail`` to override the
  system-default ``mail_location``)
* long-running Dovecot dict server for higher-traffic sites (Open
  question: Does this even make sense? On high-traffic sites with many
  users, LDAP makes a lot of sense...)

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

#. Make the newly-installed script available in system ``PATH``::

    # ln -s /usr/local/venv-dovecot-userpassdb/bin/imap-passwd /usr/local/bin

#. Finally, configure Dovecot to use the provided ``dovecot-checkpass``
   script.
