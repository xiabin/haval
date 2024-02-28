from datetime import datetime
import hashlib
import os
from pickle import TRUE
import random
import os
import time
import urllib.parse
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import yaml

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# 请求头

yaml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')

DEBUG = False
# 请求头
headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "terminal": "GW_APP_Haval",
    "enterpriseId": "CC01",
    "brand": "1",
    "rs": "2"
}

current_file_path = os.path.abspath(__file__)

current_directory = os.path.dirname(current_file_path)

token_file_path = os.path.join(current_directory, 'token.txt')

def print_time(str):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time} {str}")

# 获取随机字符串
def get_random(length):
    characters = "abcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.choice(characters) for _ in range(length))

# 生成签名
def get_auth_sign(http_method, url, json_data, timestamp, nonce):
    add_headers = {
        "bt-auth-appkey": "7736975579",
        "bt-auth-nonce": nonce,
        "bt-auth-timestamp": timestamp,
    }
    cleaned_json_data = json_data.replace(" ", "").replace("\n", "")
    data = {"json": cleaned_json_data}
    signature_string = f"{http_method}{url}"
    for key, value in sorted(add_headers.items()):
        signature_string += f"{key.lower()}:{value}"
    if http_method == "POST":
        for key, value in sorted(data.items()):
            signature_string += f"{key.lower()}={value}"
    signature_string += "8a23355d9f6a3a41deaf37a628645c62"
    encoded_string = urllib.parse.quote(signature_string, safe='')
    encoded_signature = encoded_string.encode("utf-8")
    signature_hash = hashlib.sha256(encoded_signature).hexdigest()
    add_headers["bt-auth-sign"] = signature_hash

    return add_headers

# 获取时间戳和随机字符串
def get_time_nonce():
    nonce = get_random(16)
    timestamp = str(int(time.time() * 1000))
    return nonce, timestamp

# 获取列表
def getList(token):
    path = "/app-api/api/v1.0/community/route/queryThreadList"
    nonce,timestamp = get_time_nonce()
    operatingTime = datetime.now().strftime("%Y%m%d%H%M%S%f")
    data = f"{{\"newVersion\":\"1\",\"pageParam\":{{\"pageNo\":1,\"pageSize\":20}},\"queryParam\":{{\"boardIds\":[\"2745792177421320195\"],\"firstThreadId\":\"\",\"lastThreadId\":\"\",\"newVersion\":\"1\",\"operatingTime\":\"{operatingTime}\"}},\"sortParam\":{{\"order\":\"1\",\"type\":\"3\"}}}}"
    sign_headers = get_auth_sign("POST",path,data,timestamp, nonce)
    headers.update(sign_headers)
    headers["accessToken"] = token
    response = send_request("POST",f"https://gw-app.beantechyun.com{path}",headers,data)
    if response.status_code == 200:
        json_data = response.json()
        if json_data["description"] == "SUCCESS":
            list_data = json_data["data"]["list"][:5]
            result = [{"id": item["id"], "beanId": item["threadBasic"]["author"]["beanId"]} for item in list_data]
            return result
    else:
        print_time("请求错误")


# 签到
def sign(token):
    path = "/app-api/api/v1.0/signIn/sign"
    nonce, timestamp = get_time_nonce()
    data = f"{{\"port\":\"HJ0002\"}}"
    sign_headers = get_auth_sign("POST", path, data, timestamp, nonce)
    headers.update(sign_headers)
    #print(token)
    headers["accessToken"] = token
    response = send_request("POST",f"https://gw-app.beantechyun.com{path}", headers, data)
    str = "    每日签到: "
    if response.status_code == 200:
        description = response.json()["description"]
        print_time(str.strip() + description)
        return f"{str}{description} \n".strip()
    else:
        print_time("请求错误")
        return f"{str}请求错误 \n "


# 获取列表并点赞
def like(token):
    seconds = random.uniform(10, 15)
    time.sleep(seconds)
    ids = getList(token)
    path = "/app-api/api/v1.0/community/like"
    str = "点赞任务: \n"
    for item in ids:
        nonce, timestamp = get_time_nonce()
        data = f"{{\"id\":\"{item['id']}\",\"objs\":[{{\"attr\":\"masterId\",\"value\":\"{item['beanId']}\"}},{{\"attr\":\"mobile\",\"value\":\"\"}},{{\"attr\":\"objectId\",\"value\":\"{item['id']}\"}}],\"oprType\":1,\"port\":\"HJ0013\",\"sense\":0,\"type\":0}}"
        sign_headers = get_auth_sign("POST", path, data, timestamp, nonce)
        headers.update(sign_headers)
        headers["accessToken"] = token
        response = send_request("POST",f"https://gw-app.beantechyun.com{path}", headers, data)
        if response.status_code == 200:
            json_data = response.json()
            if json_data["description"] == "SUCCESS":
                pointResultMessage = json_data["data"]["pointResultMessage"]
                if pointResultMessage is None:
                    print_time("已经没有积分可领了哦")
                    str += "    已经没有积分可领了哦\n"
                    break
                print_time(pointResultMessage)
                str += f"    {pointResultMessage}\n"
            else:
                print_time("点赞任务执行失败！")
                str += "    点赞任务执行失败！"
        else:
            print_time("请求错误")
            str += "    请求错误\n"
        random_delay = random.uniform(3, 6)
        time.sleep(random_delay)
    return str
# 获取签到状态
def getUserSignInStatus(token):
    path = "/app-api/api/v1.0/signIn/getUserSignInStatus"
    nonce, timestamp = get_time_nonce()
    sign_headers = get_auth_sign("GET", path, "", timestamp, nonce)
    headers.update(sign_headers)
    headers["accessToken"] = token
    response = send_request("GET", f"https://gw-app.beantechyun.com{path}", headers)
    str = "状态: \n"
    if response.status_code == 200:
        json_data = response.json()
        Point = json_data["data"]["remindPoint"]
        signPoint = json_data["data"]["signPoint"]
        continueSignDays = json_data["data"]["continueSignDays"]
        print_time(f"当前积分: {Point}")
        print_time(f"签到积分: +{signPoint}")
        print_time(f"已连续签到: {continueSignDays} 天")
        str += f"    当前积分: {Point}\n    今日签到积分: +{signPoint}\n    已连续签到: {continueSignDays} 天"
    else:
        print_time("请求错误")
        str += "请求错误"
    return str

def send_request(http_method,url, headers, data=None):
    if DEBUG:
        proxies = {
            'http': 'http://127.0.0.1:8888',
            'https': 'http://127.0.0.1:8888'
        }
    else:
        proxies = None

    if DEBUG:
        verify = False
    else:
        verify = True

    if http_method == "POST":
        response = requests.post(url, headers=headers, data=data, proxies=proxies, verify=verify)
    elif http_method == "GET":
        response = requests.get(url, headers=headers, proxies=proxies, verify=verify)
    return response


def calculate_md5(str):
    data = str.lower()
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    hashed_string = md5.hexdigest()
    return hashed_string


def get_sign(ts, data):
    str = "7554709466" + "53217b9e0bd5e0fc83b9fd2dd6c02a8f" + "0301" + ts
    if data is not None:
        str += json.dumps(data, separators=(',', ':'), ensure_ascii=False, sort_keys=True).strip().lower()
    #print(str)
    md5_value = calculate_md5(str)
    return md5_value

def get_headers(timestamp,data):
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "rs": "3",
        "fv": "0301",
        "vin": "LGWEF5A55LH287117",
        "sn": "QCFAXAABDN2010210375",
        "model": "24",
        "appId": "7554709466",
        "appSecret":"53217b9e0bd5e0fc83b9fd2dd6c02a8f",
        "ts": timestamp,
        "sign": get_sign(timestamp,data)
    }

    return headers


def refreshToken(userToken):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    data = {
        "accessToken": userToken.get("accessToken"),
        "refreshToken": userToken.get("refreshToken")
    }
    request_headers = get_headers(ts,data)
    response = send_request("POST","https://gw-hu.beantechyun.com/api/v1.0/userAuthService/refreshToken",request_headers,json.dumps(data))
    if response.status_code == 200:
        response_json = response.json()
        description = response_json["description"]
        if description == "SUCCESS":
            data = response_json["data"]
            accessToken = data["accessToken"]
            refreshToken = data["refreshToken"]
            accessTokenExpireDateStr = data["accessTokenExpireDateStr"]
            userToken["accessToken"] = accessToken
            userToken["refreshToken"] = refreshToken
            userToken["expireDateStr"] = accessTokenExpireDateStr
            return accessToken
        else:
            print_time(f"刷新Token失败:{description}")
            return None
    else:
        print_time("请求错误")
        return None

def login(userToken):
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    data = {
        "account": userToken.get("account"),
        "password": userToken.get("password"),
        "deviceId": "LGWEF5A55LH287117"
    }
    request_headers = get_headers(ts,data)
    response = send_request("POST","https://gw-hu.beantechyun.com/api/v1.0/userAuthService/loginAccount",request_headers,json.dumps(data))
    if response.status_code == 200:
        response_json = response.json()
        description = response_json["description"]
        if description == "SUCCESS":
            response_data = response_json["data"]
            accessToken = response_data["accessToken"]
            refreshToken = response_data["refreshToken"]
            accessTokenExpireDateStr = response_data["accessTokenExpireDateStr"]
            userToken["accessToken"] = accessToken
            userToken["refreshToken"] = refreshToken
            userToken["expireDateStr"] = accessTokenExpireDateStr
            return accessToken, None
        else:
            print_time(f"请求Token失败:{description}")
            return None, description
    else:
        print_time("请求错误")
        return None, "请求错误"


def mainTask(token,pushplus):
    message = "智家签到: \n"
    print_time("执行签到")
    message += sign(token)
    print_time("执行点赞")
    message += like(token)
    print_time("查询用户签到、积分信息")
    message += getUserSignInStatus(token)
    #print(message)
    # if pushplus is not None:
    #     print_time("发送通知")
    #     send_push(pushplus,message)


def send_push(pushplus,message):
    if pushplus is not None:
        data = {
            "title": "智家签到",
            "channel": "wechat",
            "template": "html",
            "content": message,
            "token":pushplus
        }
        send_request("POST", f"https://www.pushplus.plus/api/send", None, data=data)


def run(userTokens):
    isUpdate = False
    account = userTokens.get("account")
    pushplus = userTokens.get("pushplus")
    print_time(f"------{account}------")
    parsed_time = datetime.strptime(userTokens.get("expireDateStr"), "%Y%m%d%H%M%S%f")
    current_time = datetime.now()
    time_difference = parsed_time - current_time
    if time_difference.days < 3:
        isUpdate = True
        refreshToken(userTokens)
    token = userTokens.get("accessToken")
    mainTask(token,pushplus)
    return isUpdate

def main():

    # 获取当前脚本的目录
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # 要读取的文件名
    file_name = "config.yaml"  # 替换为实际的文件名

    # 构建文件的完整路径
    file_path = os.path.join(current_directory, file_name)
    # 读取YAML文件
    with open(file_path, 'r') as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    entries = data if isinstance(data, list) else [data]
    for entry in entries:
        entry["account"] = os.environ.get("ACCOUNT")
        entry["password"] = os.environ.get("PASSWORD")
        isUpdate = run(entry)
        if isUpdate:
            with open(file_path, 'w') as updated_yaml_file:
                yaml.dump(entries, updated_yaml_file, default_style='"')


if __name__ == "__main__":
    main()