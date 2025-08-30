import os
import requests
import json
import hashlib
import uuid
import time
import re
import urllib.parse
import urllib.parse
import string
import secrets
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import urlparse, parse_qsl

load_dotenv()


class GWM:
    def __init__(self, device_id: str, gw_id: str, model: str, username: str, password: str):
        self.app_key = os.getenv("APP_KEY")
        self.app_secret = os.getenv("APP_SECRET")

        self.device_id = device_id
        self.gw_id = gw_id
        self.model = model
        self.username = username
        self.password = password

        self.auth_prefix = "bt"

        self.success_code = "000000"
        self.token_expired_code = "550004"
        self.login_elsewhere_code = "607501"
        self.error_code = [
            self.token_expired_code,
            self.login_elsewhere_code
        ]

        self.base_url = "https://ap-h5-gateway.gwmcloud.com"

        self.session = requests.Session()
        self.session.verify = True

        try:
            self.accessToken = json.load(open('gwm_login.json', 'r'))[
                'response']['data']['accessToken']
        except:
            self.login()
            self.accessToken = json.load(open('gwm_login.json', 'r'))[
                'response']['data']['accessToken']

        pts = self.getPoint()

        if pts['code'] in self.error_code:
            self.login()

        self.current_pts = pts.get('data', '0')

    def generate_nonce(self) -> str:
        """Generate a nonce"""
        return str(uuid.uuid4()).replace('-', '')[:16]

    def generate_proper_headers(self, method: str, url: str, body: dict = None, access_token: str = "") -> dict:
        """Generate headers using decompiled apk as the reference (loginAccountDto)"""

        def generate_nonce_proper(length: int = 16) -> str:
            alphabet = string.ascii_uppercase + string.digits
            return ''.join(secrets.choice(alphabet) for _ in range(length))

        def format_request_params(method: str, url: str, body: dict = None) -> str:
            parsed_url = urlparse(url)
            if method.upper() == 'POST':

                if not body:
                    return "json={}"
                compact_json = json.dumps(body, separators=(',', ':'))
                return re.sub(r'\s', '', f"json={compact_json}")
            elif method.upper() == 'GET' and parsed_url.query:
                params = parse_qsl(parsed_url.query, keep_blank_values=True)
                param_dict = dict(params)
                sorted_keys = sorted(param_dict.keys())
                result_parts = []
                for key in sorted_keys:
                    result_parts.append(f"{key.lower()}={param_dict[key]}")
                return "".join(result_parts)
            return ""

        parsed_url = urlparse(url)
        url_path = parsed_url.path

        timestamp = str(int(time.time() * 1000))
        nonce = generate_nonce_proper()

        auth_string_part = (
            f"{self.auth_prefix}-auth-appkey:{self.app_key}"
            f"{self.auth_prefix}-auth-nonce:{nonce}"
            f"{self.auth_prefix}-auth-timestamp:{timestamp}"
        )

        formatted_params = format_request_params(method, url, body)

        base_string = (
            f"{method.upper()}"
            f"{url_path}"
            f"{auth_string_part}"
            f"{formatted_params}"
            f"{self.app_secret}"
        )

        cleaned_string = re.sub(r'\s', '', base_string)
        encoded_string = urllib.parse.quote_plus(cleaned_string)

        signature = hashlib.sha256(encoded_string.encode('utf-8')).hexdigest()

        headers = {
            f'{self.auth_prefix}-auth-appkey': self.app_key,
            f'{self.auth_prefix}-auth-timestamp': timestamp,
            f'{self.auth_prefix}-auth-nonce': nonce,
            f'{self.auth_prefix}-auth-sign': signature,
            'accessToken': access_token,
            'deviceId': self.device_id,
            'iccid': self.device_id,
            'secVersion': '2.0',
            'rs': '2',
            'appId': '1',
            'enterpriseId': 'CC01',
            'timeZone': 'GMT+07:00',
            'terminal': 'GW_APP_Haval',
            'country': 'TH',
            'brand': '1',
            'language': 'th',
            'channel': 'APP',
            'systemType': '1',
            'communityBrand': '',
            'regionCode': 'TH',
            'cVer': '3.0.1',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        return headers

    def login(self):

        payload = {
            "account": self.username,
            "password": self.password,
            "agreement": [1, 2],
            "smsCode": None,
            "msgType": None,
            "model": self.model,
            "type": 1,
            "deviceId": self.device_id,
            "appType": 0,
            "pushToken": "",
            "country": "TH",
            "countryCode": None,
            "isEncrypt": False
        }

        full_url = self.base_url + "/app-api/api/v1.0/userAuth/loginAccount"

        try:
            headers = self.generate_proper_headers(
                method="POST",
                url=full_url,
                body=payload,
                access_token=""
            )

            response = self.session.post(
                full_url,
                headers=headers,
                json=payload,
                timeout=15,
                verify=True
            )
            try:
                resp_data = response.json()

                if response.status_code == 200:
                    if resp_data.get("code") == "000000":
                        print(f"\nLogin Successfully!")
                        success_config = {
                            "timestamp": datetime.now().isoformat(),
                            "username": self.username,
                            "encryption": "RSA",
                            "headers": "main.py method",
                            "payload": payload,
                            "response": resp_data
                        }

                        with open("gwm_login.json", "w") as f:
                            json.dump(success_config, f, indent=2,
                                      ensure_ascii=False)

                    else:
                        print(f"\nLogin failed - API returned error")
                        error_msg = resp_data.get(
                            "message", resp_data.get("msg", "Unknown error"))
                        print(f"   Error: {error_msg}")

                else:
                    print(f"\nHTTP Error: {response.status_code}")

            except json.JSONDecodeError:
                print(f"\nResponse Text (not JSON):")
                print(response.text[:500])

        except Exception as e:
            print(f"\nRequest failed: {str(e)}")

    def getPoint(self):
        try:
            full_url = self.base_url + '/integral/api/v1.0/user-points/get'
            headers = self.generate_proper_headers(
                method="GET",
                url=full_url,
                access_token=self.accessToken
            )
            response = self.session.get(
                full_url,
                headers=headers,
                timeout=15,
                verify=True
            )
            resp_data = response.json()
            if resp_data.get('code', '#') == self.success_code:
                self.current_pts = resp_data.get('data', '0')
                return resp_data
            else:
                return resp_data
        except:
            self.login(self.username, self.password)
            self.getPoint()

    def addPoint(self, task_code="TH10020003", business_id="DAILY_CHECK_IN"):
        full_url = self.base_url + '/point-task/api/v1.0/task/add/addPoint'

        request_body = {
            "businessId": business_id,
            "taskCode": task_code,
            "gwid": self.gw_id,
            "platform": "01"
        }

        transaction_number = str(uuid.uuid4()).replace('-', '')
        request_no = str(uuid.uuid4()).replace('-', '')

        headers = self.generate_proper_headers(
            method="POST",
            url=full_url,
            body=request_body,
            access_token=self.accessToken
        )

        headers.update({
            'transactionNumber': transaction_number,
            'request_no': request_no,
            'brandId': '1',
            'Content-Type': 'application/json'
        })

        response = self.session.post(
            full_url,
            headers=headers,
            json=request_body,
            timeout=15,
            verify=True
        )

        try:
            return response.json()
        except:
            print(f"Response text: {response.text}")


def main():

    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    device_id = os.getenv("DEVICE_ID")
    gw_id = os.getenv("GW_ID")
    model = os.getenv("MODEL")

    gwm = GWM(
        device_id,
        gw_id,
        model,
        username,
        password
    )

    print(f"You have {gwm.current_pts} point(s).\n")

    add_point = gwm.addPoint()
    if add_point == gwm.success_code:
        print("Check in successfully!")
    else:
        print(
            f"Check in failed ({add_point["code"]}: {add_point["description"]})")


if __name__ == "__main__":
    main()
