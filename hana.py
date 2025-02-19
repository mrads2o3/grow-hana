import requests
import json
import time
from datetime import datetime
import math
import logging

def refresh_access_token(refresh_token):
    url = f"https://securetoken.googleapis.com/v1/token?key=AIzaSyDipzN0VRfTPnMGhQ5PSzO27Cxm3DohJGY"

    headers = {
        "Content-Type": "application/json",
    }

    body = json.dumps({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    })

    response = requests.post(url, headers=headers, data=body)

    if response.status_code != 200:
        error_response = response.json()
        raise Exception(f"Failed to refresh access token: {error_response['error']}")

    return response.json()

def load_refresh_token_from_file():
    try:
        with open("tokens.json", "r") as token_file:
            tokens = json.load(token_file)
            return tokens[0].get("refresh_token")
    except FileNotFoundError:
        logging.error("File 'tokens.json' not found.")
        print(Fore.RED + Style.BRIGHT + "File 'tokens.json' tidak ditemukan." + Style.RESET_ALL)
        exit()
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from 'tokens.json'.")
        exit()

def waitCountDown(sleepTime):
    print(f'Wait for {sleepTime} second')
    waitTimes = math.ceil(sleepTime / 10)
    for m in range(sleepTime, 0, -(waitTimes)):
        print(f"{m} second left", end='\r')
        time.sleep(waitTimes)

def main():
    refresh_token = load_refresh_token_from_file()
    access_token_info = refresh_access_token(refresh_token)
    access_token = access_token_info["access_token"]
    refresh_token = access_token_info.get("refresh_token", refresh_token)
    loop = True
    while loop:
        currentTime = datetime.now()
        formattedTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        print("Try to grow...", end='\r')
        try:
            hana_url = "https://hanafuda-backend-app-520478841386.us-central1.run.app/graphql"
            hana_headers = {
                'Authorization': f"Bearer {access_token}",
                'Origin': 'https://hanafuda.hana.network',
                'Referer': 'https://hanafuda.hana.network/'
            }
            hana_body = {"query":"mutation ExecuteGrowAction($withAll: Boolean) {\n  executeGrowAction(withAll: $withAll) {\n    baseValue\n    leveragedValue\n    totalValue\n    multiplyRate\n  }\n}","variables":{"withAll":True}}

            response = requests.post(hana_url, json=hana_body, headers=hana_headers)
            res = response.json()

            if res["data"]:
                resData = res["data"]
                growAction = resData["executeGrowAction"]
                print("----------------- Result -----------------")
                print(f"+ Base Value      : {growAction.get('baseValue')}")
                print(f"+ Leveraged Value : {growAction.get('leveragedValue')}")
                print(f"+ Total Value     : {growAction.get('totalValue')}")
                print(f"+ Multiply Rate   : {growAction.get('multiplyRate')}")
                print(f"+ Time            : {formattedTime}")
                print("------------------------------------------")
                print("Grow complete...")
                waitCountDown(1800)
            else :
                error_code = res["errors"][0]["extensions"]["code"]
                if error_code == "UNAUTHORIZED":
                    print("Unauthorized, try running again...", end='\r')
                    main()
                elif error_code == "NO_ACTION_COUNTS_REMAINING":
                    print(f"{formattedTime} : No action counts remaining...")
                    waitCountDown(60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)
            main()
main()