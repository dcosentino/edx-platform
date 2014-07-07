from social.backends.oauth import BaseOAuth2, BaseOAuth1
from social.backends import google
import base64


class ECOOpenIdBackend(google.GoogleOAuth2):
    """ECOOpendId authentication backend"""
    name = 'ecoopenid-auth'
    REDIRECT_STATE = False
    AUTHORIZATION_URL = 'http://ecoidp.test.reimeritsolutions.nl/authorize'
    ACCESS_TOKEN_URL = 'http://ecoidp.test.reimeritsolutions.nl/token'
    ACCESS_TOKEN_METHOD = 'POST'
    REVOKE_TOKEN_URL = 'http://ecoidp.test.reimeritsolutions.nl/token'
    REVOKE_TOKEN_METHOD = 'GET'
    DEFAULT_SCOPE = ['openid','profile','email']
    EXTRA_DATA = ['access_token','token_type','expires_in','id_token', 'refresh_token']

    def auth_headers(self):
        return {
            'Authorization': 'Basic {0}'.format(base64.urlsafe_b64encode(
                ('{0}:{1}'.format(*self.get_key_and_secret()).encode())
            ))
    }

    def get_user_id(self, details, response):
        """Use sub as unique id"""
        for p in response:
            print p,":",response[p]
        return response['sub']
    
    def user_data(self, access_token, *args, **kwargs):
        """Return user data from Google API"""
        return self.get_json(
            'http://ecoidp.test.reimeritsolutions.nl/userinfo',
            headers={'Authorization': 'Bearer {0}'.format(access_token)}
        )

