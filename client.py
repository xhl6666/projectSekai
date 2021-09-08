from Crypto.Cipher import AES,PKCS1_v1_5
from Crypto.PublicKey import RSA
import msgpack
import uuid
import requests
import base64
import json

class SekaiUser(object):
    
    def __init__(self, uid, credit):
        self.uid = uid
        self.credential = credit
        

class SekaiClient(object):
    
    def __init__(self, user:SekaiUser=None):
        self.urlroot = "http://production-game-api.sekai.colorfulpalette.org/api"
        self.urlroot2 = "https://production-game-api.sekai.colorfulpalette.org/api"
        self.headers = {
            "Content-Type": "application/octet-stream",
            "Accept": "application/octet-stream",
            "Accept-Encoding": "deflate, gzip",
            "Host": "production-game-api.sekai.colorfulpalette.org",
            "User-Agent": "UnityPlayer/2019.4.3f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
            "X-Install-Id": "baf5217d-a4d6-42b3-8c28-c4652337721b",
            "X-App-Version": "1.9.0",
            "X-Asset-Version": "1.9.0.10",
            "X-Data-Version": "1.9.0.10",
            "X-Platform": "Android",
            "X-GA": "e81d8234-b443-4193-9891-0a736c4b1546",
            "X-DeviceModel": "Xiaomi M114514C",
            "X-OperatingSystem": "Android OS 10 / API-29 (HUAWEISEA-AL10/10.1.0.164C00)",
            "X-MA": "F8:9A:78:5F:C8:04",
            "X-Unity-Version": "2019.4.3f1",
            "X-AI": "20f48346fad7f921245a8db7fdfb734f"
        }
        self.headers["X-Request-Id"] = str(uuid.uuid1())
        self.user = user
        
    @staticmethod
    def pack(content):
        mode = AES.MODE_CBC
        key = b"g2fcC0ZczN9MTJ61"
        iv = b"msx3IV0i9XE5uYZ1"
        cryptor = AES.new(key,mode,iv)
        ss = msgpack.packb(content)
        padding = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16).encode()
        ss = padding(ss)
        return cryptor.encrypt(ss)
    
    @staticmethod
    def unpack(encrypted):
        mode = AES.MODE_CBC
        key = b"g2fcC0ZczN9MTJ61"
        iv = b"msx3IV0i9XE5uYZ1"
        cryptor = AES.new(key, mode, iv)
        plaintext = cryptor.decrypt(encrypted)
        return msgpack.unpackb(plaintext[:-plaintext[-1]],strict_map_key = False)

    def callapi(self, apiurl, method, content=None):
        content = None if not content else self.pack(content)
        resp = requests.request(method, url=self.urlroot2+apiurl, headers=self.headers, data=content, timeout=5)
        return self.unpack(resp.content)

    def calluserapi(self, uid, apiurl, method, content=None):
        return self.callapi(f"/user/{uid}{apiurl}", method, content)
    
    def register(self) -> SekaiUser:
        data = self.callapi("/user", "POST", {'platform': self.headers["X-Platform"], 'deviceModel': self.headers["X-DeviceModel"], 'operatingSystem': self.headers["X-OperatingSystem"]})
        credential = data["credential"]
        uid = data["userRegistration"]["userId"]
        self.user = SekaiUser(uid, credential)
        return self.user
        
    def login(self):
        data = self.calluserapi(self.user.uid, "/auth?refreshUpdatedResources=False", "PUT", {"credential": self.user.credential})
        self.token = data["sessionToken"]
        self.headers["X-Session-Token"] = self.token
        self.update_headers()
        return self.token
    
    def update_headers(self):
        data = self.callapi("/system", "GET")
        for v in data["appVersions"]:
            if not v["appVersionStatus"] == "available": continue
            self.headers["X-Data-Version"] = v["dataVersion"]
            self.headers["X-Asset-Version"] = v["assetVersion"]
            self.headers["X-App-Version"] = v["appVersion"]
    
    def get_profile(self, uid:str):
        data = self.calluserapi(uid, "/profile", "GET")
        return data
        
    def test(self):
        pass

    
# user = SekaiUser("129502785700777984", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjcmVkZW50aWFsIjoiZmZiZGZmNGMtZDQ2My00ZjIxLThlMzMtOGQ5NDE2NzY4MjA0IiwidXNlcklkIjoiMTI5NTAyNzg1NzAwNzc3OTg0In0.Z-jZk0kd-8YxuKjXxvGFJAWlgDzmSh0NElgqqOlf_5Q")
# sekai = SekaiClient(user)
# # sekai.register()
# sekai.login()
# a = sekai.get_profile("5557466289360906")

