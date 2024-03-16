import re
import time
import threading
from bs4 import BeautifulSoup
import requests
import random
import string
import json
import phonenumbers
import base64
import pyotp
from mailtm import Email
from capsolver_python import RecaptchaV3Task
import urllib3
import urllib.parse
from urllib.parse import unquote
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

lock = threading.Lock()

sms_apikey = ""
captcha_apikey = ""

class Generator:
    def __init__(self, proxy=""):
        self.proxy = proxy
        self.ubiSoft = self._ubiSoft()
        self.username = self.generate_username()
        self.password = self.generate_password()
        self.authorization = ""
        self.numberID = None
        self.mailBox = Email()
        self.mailBox.register(self.username, self.password)
        self.mail = self.mailBox.address
        self.mailToken = self.mailBox.token
        self.recoveryCodes = []
    def _ubiSoft(self):
        ubiSoft = type('ubiSoft', (), {})
        ubiSoft.START_CHANGE_EMAIL = "start_change_email"
        ubiSoft.FINISH_CHANGE_EMAIL = "finish_change_email"
        ubiSoft.START_VERIFY_EMAIL = "email_verify_start"
        ubiSoft.FINISH_VERIFY_EMAIL = "email_verify_complete"
        ubiSoft.START_PHONE_ACTIVATION = "start_phone_number"
        ubiSoft.FINISH_PHONE_ACTIVATION = "finish_phone_number"
        ubiSoft.SEND_PHONE_CODE = "send_new_code_phone_number"
        ubiSoft.START_ACTIVATE_2FA_AUTH = "start_2FA_authenticator"
        ubiSoft.PROCESS_2FA_AUTH = "process_2FA_authenticator"
        ubiSoft.START_ACTIVATE_2FA_EMAIL = "start_2FA_email"
        ubiSoft.START_ACTIVATE_2FA_SMS = "start_2FA_SMS"
        ubiSoft.FINISH_ACTIVATE_AUTH = "finish_2FA_authenticator"
        ubiSoft.FINISH_ACTIVATE_EMAIL = "finish_2FA_email"
        ubiSoft.FINISH_ACTIVATE_SMS = "finish_2FA_SMS"
        ubiSoft.GENERATE_2FA_CODES = "generate_2FA_codes"
        ubiSoft.recaptchaScoreBasedSiteKey = "6LfKjOsnAAAAAJ_j9l9j7x1EaAZ57QJsuxGyTYko"
        ubiSoft.recaptchaFinishChangeEmailChallengeSiteKey = "6LfQJUIfAAAAAMSCs6AlMvszHuLmbnHyEAWw21XZ"
        ubiSoft.recaptchaStartEmailChangeChallengeSiteKey = "6Lex0eInAAAAAC0H_zH3Av_ewmXTXjsE31jogfKo"
        ubiSoft.recaptchaStartEmailVerifyChallengeSiteKey = "6LfHyOInAAAAABI7_08h7O3Vj7-n4vDoFRM_YCZ1"
        ubiSoft.recaptchaFinishEmailVerifyChallengeSiteKey = "6LeZR6snAAAAAHnkDvfGSFp51ghEOi1RXFAvxBIJ"
        ubiSoft.recaptchaStartPhoneActivationChallengeSiteKey = "6LcRAcYnAAAAAI2-GdQ-gS_zaee_5rZj6DAEa2Mu"
        ubiSoft.recaptchaSendPhoneCodeChallengeSiteKey = "6LeM0sgnAAAAAD6MLlkcdu3X2M_Pbs6ZWHTnEWhE"
        ubiSoft.recaptchaFinishPhoneActivationChallengeSiteKey = "6LdPvMgnAAAAAMvHly4Ai-PAa4Kzu1uvrO1S32OU"
        ubiSoft.recaptchaStartTwoActivationFAChallengeSiteKey = "6LcotOInAAAAADCBXkDqtg8frAJ6Lg_IMYHhsNv6"
        ubiSoft.recaptchaProcessTwoFAChallengeSiteKey = "6LevneMnAAAAADC8Fk2ynqnzR1hwk0R_tR93iF56"
        ubiSoft.recaptchaActivateTwoFAChallengeSiteKey = "6LdBLuQnAAAAAGuNFEfw3_5jJqAV2A-FCkW7LAKI"
        ubiSoft.recaptchaGenerateTwoFACodesChallengeSiteKey = "6LfFcBYbAAAAAO4OIi439ZWS5Y5vhkUjnHQVILMl"
        return ubiSoft
    
    def generate_password(self):
        uppercase_chars = string.ascii_uppercase
        lowercase_chars = string.ascii_lowercase
        digit_chars = string.digits
        special_chars = "!+&"
        password = random.choice(uppercase_chars) + random.choice(uppercase_chars)
        while len(password) < 7:
            password += random.choice(lowercase_chars)
        password += random.choice(digit_chars)
        password += random.choice(special_chars)
        password += "@"
        password = "".join(random.sample(password, len(password)))
        return password

    def generate_username(self, length=10):
        characters = string.ascii_lowercase
        random_string = "".join(random.choice(characters) for _ in range(length))
        return random_string

    def generate_ubi_challenge(self, action):

        capsolver = RecaptchaV3Task(captcha_apikey)
        task_id = capsolver.create_task(
            "https://account.ubisoft.com/en-US/security-settings/two-factor-authentication",
            "6LfKjOsnAAAAAJ_j9l9j7x1EaAZ57QJsuxGyTYko",
            action,
            0.8,
        )
        try:
            result = capsolver.join_task_result(task_id)

            if len(result.get("gRecaptchaResponse")) > 0:
                token = result.get("gRecaptchaResponse")
                input_string = (
                    f"sitekey={self.ubiSoft.recaptchaScoreBasedSiteKey}&token={token}"
                )
                encoded_string = base64.b64encode(input_string.encode("utf-8")).decode(
                    "utf-8"
                )
                return "cce=" + encoded_string
            else:
                return None
        except:
            return None

    def get_number(self):
        response = requests.post(
            f"https://smshub.org/stubs/handler_api.php?api_key={sms_apikey}&action=getNumber&service=ot&maxPrice=2&country=16&operator=ee"
        )
        if "ACCESS_NUMBER" in response.text:
            return [response.text.split(":")[1], response.text.split(":")[2]]
        else:
            return None, None

    def getNumberResponse(self):
        response = requests.post(
            f"https://smshub.org/stubs/handler_api.php?api_key={sms_apikey}&action=getStatus&id="
            + self.numberID
        )
        if "STATUS_OK:" in response.text:
            text = response.text.split(":")[1]
            pattern = r"\b\d{6}\b"
            digit_codes = re.findall(pattern, text)
            if digit_codes:
                return digit_codes[0]
            return
        else:
            return None

    def removeNumber(self):
        requests.post(
            f"https://smshub.org/stubs/handler_api.php?api_key={sms_apikey}&action=setStatus&id="
            + self.numberID
            + "&status=8"
        )

    def verifyPhoneNumber(self):

        while self.numberID is None:
            self.numberID, self.number = (self.get_number())
            time.sleep(0.2)

        parsed_number = phonenumbers.parse("+" + self.number, None)
        country_code = parsed_number.country_code

        url = "https://public-ubiservices.ubi.com/v3/users/me/startPhoneActivation"
        payload = json.dumps(
            {
                "phoneNumber": parsed_number.national_number,
                "countryCallingCode": country_code,
            }
        )

        headers = {
            "authorization": self.authorization,
            "content-type": "application/json",
            "ubi-appid": "c5393f10-7ac7-4b4f-90fa-21f8f3451a04",
            "ubi-challenge": self.generate_ubi_challenge(
                self.ubiSoft.START_PHONE_ACTIVATION
            ),
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        }
        proxies = {"http": self.proxy, "https": self.proxy}
        
        while True:
            try:
                response = requests.request(
                    "POST",
                    url,
                    headers=headers,
                    data=payload,
                    proxies=proxies,
                    verify=False,
                )
                break
            except:
                time.sleep(0.3)

        if response.status_code == 200:
            response = None
            validationCode = None
            t_start = time.time()
            while (time.time() - t_start) < 45:
                validationCode = self.getNumberResponse()
                if not validationCode == None:
                    break
            if validationCode == None:
                self.removeNumber()
                self.numberID = None
                self.number = None
                return self.verifyPhoneNumber()

            url = (
                "https://public-ubiservices.ubi.com/v3/users/me/completePhoneActivation"
            )
            payload = json.dumps(
                {
                    "phoneNumber": parsed_number.national_number,
                    "countryCallingCode": country_code,
                    "phoneValidationCode": validationCode,
                }
            )

            headers = {
                "authorization": self.authorization,
                "content-type": "application/json",
                "ubi-appid": "c5393f10-7ac7-4b4f-90fa-21f8f3451a04",
                "ubi-challenge": self.generate_ubi_challenge(
                    self.ubiSoft.FINISH_PHONE_ACTIVATION
                ),
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36",
            }
            proxies = {"http": self.proxy, "https": self.proxy}

            while True:
                try:
                    response = requests.request(
                        "POST", url, headers=headers, data=payload, proxies=proxies
                    )
                    break
                except:
                    time.sleep(0.3)

            return response.status_code == 200
        else:
            if (
                "The phone number is not accepted due to high risk score"
                in response.json()["message"]
            ):
                self.deleteNumber()
                self.numberID = None
                self.number = None
                return self.verifyPhoneNumber()

            print(f"Request Failed {response.text}")

    def Set2FA(self):
        url = "https://public-ubiservices.ubi.com/v3/profiles/me/start2faActivation"
        payload = json.dumps({"codeGenerationPreference": "googleAuthenticator"})
        headers = {
            "authorization": self.authorization,
            "content-type": "application/json",
            "ubi-appid": "c5393f10-7ac7-4b4f-90fa-21f8f3451a04",
            "ubi-challenge": self.generate_ubi_challenge(
                self.ubiSoft.START_ACTIVATE_2FA_AUTH
            ),
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36",
        }
        proxies = {"http": self.proxy, "https": self.proxy}

        while True:
            try:
                response = requests.post(url, headers=headers, data=payload, proxies=proxies)
                break
            except:
                time.sleep(0.3)

        if response.status_code == 200:
            token_code = ""

            while len(token_code) == 0:
                for realMsg in self.mailBox.message_list():
                    message = self.mailBox.message(realMsg["id"])
                    time.sleep(1)
                    if "2-Step Verification Activation" in message["subject"]:
                        soup = BeautifulSoup(message["html"][0], "html.parser")
                        all_links = soup.find_all("a")
                        for link in all_links:
                            href = link.get("href")
                            href = unquote(href)
                            if href and "modal=activate-2fa-step1/1/" in href:
                                query_parameters = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                                token = query_parameters.get("token", [None])[0]
                                token_code = token
                                break
                if len(token_code) == 0:
                    time.sleep(3)

            url = "https://public-ubiservices.ubi.com/v3/profiles/me/2fa"
            payload = json.dumps({"2faActivationKey": token_code})
            headers = {
                "authorization": self.authorization,
                "content-type": "application/json",
                "ubi-appid": "c5393f10-7ac7-4b4f-90fa-21f8f3451a04",
                "ubi-challenge": self.generate_ubi_challenge(
                    self.ubiSoft.PROCESS_2FA_AUTH
                ),
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36",
            }
            proxies = {"http": self.proxy, "https": self.proxy}
            while True:
                try:
                    response = requests.post(url, headers=headers, data=payload, proxies=proxies)
                    break
                except:
                    time.sleep(0.3)
            if response.status_code == 200:
                secretCode = response.json()["secret"]
                totp = pyotp.TOTP(secretCode)
                url = "https://public-ubiservices.ubi.com/v3/profiles/me/2fa"
                payload = json.dumps(
                    {
                        "codeGenerationPreference": "googleAuthenticator",
                        "sendsRecoveryCodesByEmail": True,
                    }
                )
                headers = {
                    "authorization": self.authorization,
                    "content-type": "application/json",
                    "ubi-appid": "c5393f10-7ac7-4b4f-90fa-21f8f3451a04",
                    "ubi-challenge": self.generate_ubi_challenge(
                        self.ubiSoft.FINISH_ACTIVATE_AUTH
                    ),
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36",
                    "ubi-2facode": totp.now(),
                }
                proxies = {"http": self.proxy, "https": self.proxy}
                while True:
                    try:
                        response = requests.put(url, headers=headers, data=payload, proxies=proxies)
                        break
                    except:
                        time.sleep(0.3)
                if response.status_code == 200:
                    self.recoveryCodes = [
                        item["code"] for item in response.json()["recoveryCodes"]
                    ]
                    with lock:
                        with open("acc.txt", "a") as myfile:
                            myfile.write(f"{self.mail}|{self.password}|{secretCode}\n")


                return response.status_code == 200
                """
                {"recoveryCodes":[{"code":"NVQDHU"},{"code":"MVBWZV"},{"code":"DFYEMH"},{"code":"ESGSMN"},{"code":"GGSSYN"},{"code":"AAZDXH"}]}
                """
            else:
                print(f"Request Failed {response.text}")

    def createAccount(self):
        proxies = {"http": self.proxy, "https": self.proxy}
        while True:
            try:
                accountResponse = requests.post(
                    "https://public-ubiservices.ubi.com/v3/users",
                    proxies=proxies,
                    json={
                        "legalOptinsKey": "eyJ2dG91IjoiNC4wIiwidnBwIjoiNC4wIiwidnRvcyI6IjIuMCIsImx0b3UiOiJlbi1DQSIsImxwcCI6ImVuLUNBIiwibHRvcyI6ImVuLUNBIn0",
                        "email": f"{self.mail}",
                        "nameOnPlatform": self.username,
                        "country": "CA",
                        "preferredLanguage": "en",
                        "dateOfBirth": f"{random.randint(1990, 2005)}-05-01T00:00:00.0000000+00:00",
                        "password": self.password,
                    },
                    headers={
                        "Ubi-Appid": "f68a4bb5-608a-4ff2-8123-be8ef797e0a6",
                        "Ubi-RequestedPlatformType": "uplay",
                        "User-Agent": "Massgate",
                    },
                )
                break
            except:
                time.sleep(0.3)
        if accountResponse.status_code == 200:
            print(f"{self.mail}")
            print(f"{self.password}")
            self.authorization = "Ubi_v1 t=" + accountResponse.json()["ticket"]
        else:
            print(accountResponse.text)
        return accountResponse.status_code == 200

    def loginAccount(self, mail, password):
        url = "https://public-ubiservices.ubi.com/v3/profiles/sessions"
        payload = json.dumps({"rememberMe": "true"})
        credentials_bytes = bytes(f"{mail}:{password}", "utf-8")
        auth = base64.b64encode(credentials_bytes).decode("utf-8")
        headers = {
            "content-type": "application/json",
            "ubi-appid": "afb4b43c-f1f7-41b7-bcef-a635d8c83822",
            "ubi-requestedplatformtype": "uplay",
            "authorization": f"Basic {auth}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        }
        proxies = {"http": self.proxy, "https": self.proxy}
        response = requests.post(url, headers=headers, data=payload, proxies=proxies, verify=False)
        if response.status_code == 200:
            self.authorization = "Ubi_v1 t=" + response.json()["ticket"]
        return response.status_code == 200
