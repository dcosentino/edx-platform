import base64
from social.backends.oauth import BaseOAuth2


class ECOOpenIdBackend(BaseOAuth2):
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
    USERINFO='http://ecoidp.test.reimeritsolutions.nl/userinfo'

    def auth_headers(self):
        return {
            'Authorization': 'Basic {0}'.format(base64.urlsafe_b64encode(
                ('{0}:{1}'.format(*self.get_key_and_secret()).encode())
            ))
    }

#    def do_auth(self, access_token, *args, **kwargs):
#        """Finish the auth process once the access_token was retrieved"""
#        data = self.user_data(access_token, *args, **kwargs)
#        response = kwargs.get('response') or {}
#        response.update(data or {})
#        client,secret=self.get_key_and_secret()
#        id_token=response.get('id_token')
#       try:  # Decode the token, using the Application Signature from settings
#            decoded = jwt.decode(id_token, secret)
#        except jwt.DecodeError:  # Wrong signature, fail authentication
#            raise AuthCanceled(self)
#        response['sub']=decoded.get('sub')
#        response['exp']=decoded.get('exp')
#        #response['nonce']=decoded.get('nonce')
#        kwargs.update({'response': response, 'backend': self})
#        return self.strategy.authenticate(*args, **kwargs)

    def get_user_details(self, response):
        """Return user details from ECO account"""
        email=response.get('email')
        return {'username': response.get('nickname'),
            'email': email,
            'fullname': response.get('name'),
            'first_name': response.get('given_name'),
            'last_name': response.get('family_name')}

    def get_user_id(self, details, response):
        """Use sub as unique id"""
        return response['sub']

    def user_data(self, access_token, *args, **kwargs):
        """Return user data from Google API"""
        values= self.get_json(self.USERINFO,
            headers={'Authorization': 'Bearer {0}'.format(access_token)}
        )
        values['username']=values['nickname']
        return values
