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
import datetime
from typing import Tuple

import jwcrypto.jwk as jwk
import python_jwt as jwt


def generate_keys() -> Tuple[bytes, bytes]:
    """Generates a private / public key pair.

    The keys are generated using the RSA algorithm with a size of 4096.

    Returns:
        A tuple containing the private key and the public key in PEM format.
    """
    keys = jwk.JWK.generate(kty="RSA", size=4096)
    priv_pem = keys.export_to_pem(private_key=True, password=None)
    pub_pem = keys.export_to_pem()

    return priv_pem, pub_pem


def generate_jwt(priv_key: jwk.JWK, user_id: int) -> str:
    """Generates a JWT token, signed with the given private key.

    Args:
        priv_key: The private key, used to sign the jwt.
        user_id: The id of the user.

    Returns:
        A JWT containing the user id. It is signed with the provided private key.
    """
    payload = {"userID": user_id}

    token = jwt.generate_jwt(payload, priv_key, "RS256", lifetime=datetime.timedelta(minutes=1))

    return token
