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

    def get_user_id(self, details, response):
        """Use codice persona as unique id"""
        return response['sub']

    def get_user_details(self, response):
        """Return user details """
        codicePersona = response.get('sub', '')
        email=codicePersona+"@polimi.it"
        fullname, first_name, last_name = self.get_user_names(
            response.get('name', ''),
            response.get('given_name', ''),
            response.get('family_name', '')
        )
        return {'username': codicePersona,
                'email': email,
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name}
