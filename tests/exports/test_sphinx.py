# -*- encoding: utf-8 -*-
# pass-import - test suite
# Copyright (C) 20220 Stefan Marsiske <sphinx@ctrlc.hu>.
#

from unittest.mock import patch

from pass_import.managers.sphinx import Sphinx
from pwdsphinx.sphinx import RULE_SIZE
from pass_import.errors import PMError
from pwdsphinx import sphinx as pwdsphinx

import tests

class MockCreateSock:
    state = 0
    actions = (
        ('send', 65),              # recv 0x00|id[32]|alpha[32]
                                   # send beta[32]
        ('recv', b'\xaa\x16\xc7?\x81\xf1\xf9qw\x00\x0b\x1b\xdb\x0bA\xcf\x19\xce\xeb_O\xe3\x99\xe5G\xb8M\xa9\x1a\xbcKM'),
        ('send', 32+RULE_SIZE+64),  # pubkey, rule, signature
        ('send', 32+64),           # id + signature
        ('recv', b"\x00\x00"),
        ('send', 0),               # pk[32], size[2], pkt[size], signature[64]
        ('recv', 'ok')
    )

    def send(self, pkt):
        action = self.actions[self.state]
        assert action[0] == 'send'
        if action[1]: assert len(pkt) == action[1]
        self.state+=1

    def recv(self, size):
        action = self.actions[self.state]
        assert action[0] == 'recv'
        assert size == len(action[1])
        self.state+=1
        return action[1]

    def close(self):
        return

def connect():
    return MockCreateSock()
pwdsphinx.connect = connect

class TestExportSphinx(tests.Test):
    """Test sphinx general features."""
    def setUp(self):
        self.sphinx = Sphinx(self.prefix)

    def test_sphinx_exist(self):
        """Testing: exist."""
        self.assertTrue(self.sphinx.exist())

    def test_sphinx_isvalid(self):
        """Testing: isvalid."""
        self.assertTrue(self.sphinx.isvalid())

class TestExportSphinxInsert(tests.Test):
    """Test Sphinx insert features."""

    @patch("getpass.getpass")
    def test_sphinx_insert(self, pw):
        """Testing: sphinx insert."""
        pw.return_value = self.masterpassword
        entry = {
            'password': 'UuQHzvv6IHRIJGjwKru7',
            'login': 'lnqYm3ZWtm',
            'url': 'https://twitter.com',
            'website': 'https://pujol.io',
            'uuid': '44jle5q3fdvrprmaahozexy2pi',
            'otpauth': 'otpauth://totp/totp-secret?secret=JBSWY3DPEHPK3PXP&'
                       'issuer=alice@google.com&algorithm=SHA1&digits=6&per'
                       'iod=30',
            'path': 'Test/test'
        }

        with Sphinx(self.prefix) as sphinx:
            sphinx.insert(entry)

    @patch("getpass.getpass")
    def test_sphinx_insert_empty(self, pw):
        """Testing: sphinx insert empty."""
        pw.return_value = self.masterpassword
        entry = {'path': 'test'}

        with Sphinx(self.prefix) as sphinx:
            with self.assertRaises(PMError):
                sphinx.insert(entry)
