from third_party_auth.provider import BaseProvider


class PolimiOauth2(BaseProvider):
    """Provider for Google's Oauth2 auth system."""

    BACKEND_CLASS = PolimiOAuth2Backend
    ICON_CLASS = 'icon-polimi-aunica'
    NAME = 'Polimi'
    SETTINGS = {
        'SOCIAL_AUTH_POLIMI_OAUTH2_KEY': None,
        'SOCIAL_AUTH_POLIMI_OAUTH2_SECRET': None,
    }

    @classmethod
    def get_email(cls, provider_details):
        return provider_details.get('email')

    @classmethod
    def get_name(cls, provider_details):
        return provider_details.get('fullname')