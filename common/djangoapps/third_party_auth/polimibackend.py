from social.backends.oauth import BaseOAuth2, BaseOAuth1
from social.backends import google

class PolimiOAuth2Backend(google.GoogleOAuth2):
    """Polimi OAuth2 authentication backend"""
    name = 'polimi-oauth2'
    REDIRECT_STATE = False
    AUTHORIZATION_URL = 'https://oauthidp.polimi.it/oauthidp/oauth2/auth'
    ACCESS_TOKEN_URL = 'https://oauthidp.polimi.it/oauthidp/oauth2/token'
    ACCESS_TOKEN_METHOD = 'POST'
    REVOKE_TOKEN_URL = 'https://oauthidp.polimi.it/oauthidp/oauth2/token'
    REVOKE_TOKEN_METHOD = 'GET'
    DEFAULT_SCOPE = ['openid',
                     '216']
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token', True),
        ('expires_in', 'expires'),
        ('token_type', 'token_type', True)
    ]
    
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