###############################################################################
#
# Copyright 2021 - Jan Bormet, Anna-Felicitas Hausmann, Joachim Schmidt, Vincent Stollenwerk, Arne Turuc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://www.opensource.org/licenses/mit-license.php
#
###############################################################################


from jwcrypto import jwk
import python_jwt as jwt

from timewsync import auth


def test_generate_keys():
    private_key_pem, public_key_pem = auth.generate_keys()

    assert str(private_key_pem).find("-----BEGIN PRIVATE KEY-----") != -1
    assert str(private_key_pem).find("-----END PRIVATE KEY-----") != -1

    assert str(public_key_pem).find("-----BEGIN PUBLIC KEY-----") != -1
    assert str(public_key_pem).find("-----END PUBLIC KEY-----") != -1


def test_generate_jwt():
    key = jwk.JWK.generate(kty="RSA", size=2048)

    token = auth.generate_jwt(key, 42)

    header, claims = jwt.verify_jwt(token, key, ["RS256"])

    assert claims is not None
    assert header is not None

    assert claims["userID"] == 42
    assert header["alg"] == "RS256"
    assert header["typ"] == "JWT"
