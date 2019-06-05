import sha
import urllib
import os
try:
    import threading
except ImportError:
    import dummy_threading as threading
import random

class SignatureError(Exception): pass

class SecureSigner(object):

    """
    This will sign fields, and pack the value and signature into a
    single hidden field.  You may also make the field expirable.

    Usage:

    >>> signer = securehidden.SecureSigner('/path/to/signature.txt')
    >>> secure_value = 'test'
    >>> signed = signer.secure_value(secure_value)
    >>> signed
    # 0 is the timeout (we gave no timeout):
    '0 256ac50cfc776a5d84d54f46a3ffdb8ea16664c0 test'
    >>> signer.parse_secure('signed')
    'test'
    >>> signer.parse_secure('0 256ac50cfc776a5d84d54f46a3ffdb8ea16664c0 test2')
    Traceback (most recent call last):
        ...
    securehidden.SignatureError: Bad signature: '256ac50cfc776a5d84d54f46a3ffdb8ea16664c0'
    """

    def __init__(self, secret_filename):
        self.secret_filename = secret_filename
        self._secret = None
        self.secret_lock = threading.Lock()

    def secret(self):
        if self._secret is not None:
            return self._secret
        self.secret_lock.acquire()
        try:
            if self._secret is None:
                self._generate_secret()
        finally:
            self.secret_lock.release()
        return self._secret

    def _generate_secret(self):
        if not os.path.exists(self.secret_filename):
            self._secret = ''
            for i in range(4):
                self._secret += hex(random.randrange(0xffff))[2:]
            f = open(self.secret_filename, 'w')
            f.write(self._secret)
            f.write('\n')
            f.close()
        else:
            f = open(self.secret_filename)
            self._secret = f.read().strip()
            f.close()

    def secure_value(self, value, timeout=None):
        """
        The value, signed and potentially with a timeout.  The timeout
        should be in seconds, e.g., 3600 for an hour.
        """
        pieces = []
        if timeout:
            expire = str(int(time.time()) + timeout)
        else:
            expire = '0'
        digest = sha.new()
        digest.update(value)
        digest.update(expire)
        digest.update(self.secret())
        pieces.append(expire)
        pieces.append(digest.hexdigest())
        pieces.append(value)
        return ' '.join(pieces)

    def parse_secure(self, input):
        """
        Take the value as produced by .secure_value(), unpack it, confirm
        the signature and expiration, and return the original value.  If
        something has happened -- the signature doesn't match, or it has
        expired -- a SignatureError will be raised.
        """
        expire, signature, value = input.split(' ', 2)
        digest = sha.new()
        digest.update(value)
        digest.update(expire)
        digest.update(self.secret())
        if not digest.hexdigest() == signature:
            raise SignatureError, "Bad signature: %r" % signature
        expire = int(expire)
        if expire and time.time() > expire:
            raise SignatureError, "Signature expired on %s (now is %s)" % (expire, time.time())
        return value

