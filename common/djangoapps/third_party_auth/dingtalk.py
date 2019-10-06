import time
import base64
import hmac
from hashlib import sha256
from social_core.backends.oauth import BaseOAuth2

class DingtalkOAuth2(BaseOAuth2):
    "钉钉　并不是oAuth2的接入"
    name = "dingtalk"
    AUTHORIZATION_URL = 'https://oapi.dingtalk.com/connect/qrconnect'
    ACCESS_TOKEN_URL = ''

    def auth_params(self, *args, **kwargs):
        params = super(DingtalkOAuth2, self).auth_params(*args, **kwargs)
        params['appid'] = params.pop('client_id')
        params['state'] = 'STATE'
        params['scope'] = 'snsapi_login'
        return params

    def request_access_token(self, *args, **kwargs):
        return {'access_token': self.data.get('code', '')}

    def user_data(self, access_token, *args, **kwargs):
        appid, appsecret = self.get_key_and_secret()
        now_timestamp = int(round(time.time()* 1000))
        signature = base64.b64encode(hmac.new(appsecret, now_timestamp, digestmod=sha256).digest())
        userinfo_url = 'https://oapi.dingtalk.com/sns/getuserinfo_bycode?\
                        accessKey={accessKey}&timestamp={timestamp}&signature={signature}'\
                        .format(accessKey=appid, timestamp=now_timestamp, signature=signature)
        return self.get_json(userinfo_url, method='post',
                             params={'tmp_auth_code': access_token})

    def get_user_details(self, response):
        info = response.get('user_info')
        return {
            "username": info['nick']
        }

    def get_user_id(self, details, response):
        return response.get('user_info').get('unionid')
