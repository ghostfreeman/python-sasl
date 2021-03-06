"""plain -- simple, unencrypted user/password authentication

<http://www.ietf.org/rfc/rfc4616.txt>

Copyright (c) 2009, Coptix, Inc.  All rights reserved.
See the LICENSE file for license terms and warranty disclaimer.
"""
from __future__ import absolute_import
from . import mechanism as mech, auth

__all__ = ('Plain', 'PlainPassword')

class Plain(mech.Mechanism):
    """The plain mechanism simply submits the optional authorization
    id, the authentication id, and password separated by null
    bytes."""

    NULL = u'\x00'

    def __init__(self, auth):
        self.auth = auth

    def verify(self, *args):
        return self.auth.verify_password(*args)

    state = mech.AuthState

    ## Server

    def challenge(self):
        return self.state(self.verify_challenge, None, '')

    def verify_challenge(self, entity, response):
        try:
            (zid, cid, passwd) = response.decode('utf-8').split(self.NULL)
        except ValueError as exc:
            return self.state(False, entity, None)

        try:
            entity = entity or zid or cid
            return self.state(self.verify(zid, cid, passwd), entity, None)
        except auth.PasswordError as exc:
            return self.state(False, entity, None)

    ## Client

    def respond(self, data):
        assert data == ''

        auth = self.auth
        zid = auth.authorization_id()
        cid = auth.username()

        response = self.NULL.join((
            u'' if (not zid or zid == cid) else zid,
            (cid or u''),
            (auth.password() or u'')
        )).encode('utf-8')

        self.authorized = zid or cid
        return self.state(None, zid or cid, response)

class PlainPassword(auth.PasswordType):

    @staticmethod
    def make(authenticator, user, passwd):
        (kind, secret) = auth.password_type(passwd)
        if kind == None:
            return auth.make_password('PLAIN', passwd)
        elif kind == 'PLAIN':
            return passwd
        else:
            raise auth.PasswordError('Expected PLAIN password, not %s' % kind)

