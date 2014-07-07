from social.backends.oauth import BaseOAuth2, BaseOAuth1

class ECOOpenIdBackend(BaseOAuth2):
    """ECOOpendId authentication backend"""
    name = 'ecoopenid-auth'
    REDIRECT_STATE = False
    AUTHORIZATION_URL = 'http://ecoidp.test.reimeritsolutions.nl/authorize'
    ACCESS_TOKEN_URL = 'http://ecoidp.test.reimeritsolutions.nl/token'
    ACCESS_TOKEN_METHOD = 'POST'
    REVOKE_TOKEN_URL = 'http://ecoidp.test.reimeritsolutions.nl/token'
    REVOKE_TOKEN_METHOD = 'GET'
    DEFAULT_SCOPE = ['openid']
    EXTRA_DATA = ['id_token', 'refresh_token']

    def user_data(self, access_token, *args, **kwargs):
        """Return user data from Google API"""
        return self.get_json(
            'http://ecoidp.test.reimeritsolutions.nl/userinfo',
            params={'access_token': access_token, 'alt': 'json'}
        )
