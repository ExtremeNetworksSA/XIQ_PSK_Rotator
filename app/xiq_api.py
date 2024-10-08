#!/usr/bin/env python3
import logging
import os
import inspect
import sys
import json
import time
import requests
from pprint import pprint as pp
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from requests.exceptions import HTTPError, ReadTimeout
from app.logger import logger

logger = logging.getLogger('PSK_Rotator.xiq_api')

PATH = current_dir

class APICallFailedException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class XIQ:
    def __init__(self, user_name=None, password=None, token=None):
        self.URL = "https://api.extremecloudiq.com"
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}
        self.totalretries = 5
        if token:
            self.headers["Authorization"] = "Bearer " + token
        else:
            try:
                self.__getAccessToken(user_name, password)
            except ValueError as e:
                print(e)
                raise SystemExit
            except HTTPError as e:
               print(e)
               raise SystemExit
            except:
                log_msg = "Unknown Error: Failed to generate token for XIQ"
                logger.error(log_msg)
                print(log_msg)
                raise SystemExit 
    #API CALLS
    def __setup_get_api_call(self, info, url):
        success = 0
        for count in range(1, self.totalretries):
            try:
                response = self.__get_api_call(url=url)
            except ValueError as e:
                log_msg = (f"API to {info} failed attempt {count} of {self.totalretries} with {e}")
                print(log_msg)
                logger.warning(log_msg)
            except Exception as e:
                log_msg = (f"API to {info} failed with {e}")
                logger.error(log_msg)
                raise ValueError(log_msg)
            except:
                log_msg = (f"API to {info} failed attempt {count} of {self.totalretries} with unknown API error")
                print(log_msg)
                logger.warning(log_msg)
            else:
                success = 1
                break
        if success != 1:
            log_msg = (f"failed to {info}. Cannot continue.")
            log_msg += (" Check log file for details")
            logger.error(log_msg)
            raise APICallFailedException(log_msg)
        if 'error' in response:
            if response['error']['error_message']:
                log_msg = (f"Error Code {response['error']['error_id']}: {response['error']['error_message']}")
                logger.error(log_msg)
                log_msg = (f"API Failed {info} with reason: {log_msg}")
                raise APICallFailedException(log_msg)
        return response
    
    def __setup_put_api_call(self, info, url, payload):
        success = 0
        for count in range(1, self.totalretries):
            try:
                response = self.__put_api_call(url=url, payload=payload)
            except ValueError as e:
                log_msg = (f"API to {info} failed attempt {count} of {self.totalretries} with {e}")
                print(log_msg)
                logger.warning(log_msg)
            except Exception as e:
                log_msg = (f"API to {info} failed with {e}")
                logger.error(log_msg)
                raise ValueError(log_msg)
            except:
                log_msg = (f"API to {info} failed attempt {count} of {self.totalretries} with unknown API error")
                print(log_msg)
                logger.warning(log_msg)
            else:
                success = 1
                break
        if success != 1:
            log_msg = (f"failed to {info}. Cannot continue.")
            log_msg += (" Check log file for details")
            logger.error(log_msg)
            raise APICallFailedException(log_msg)
        if 'error' in response:
            if response['error']['error_message']:
                log_msg = (f"Error Code {response['error']['error_id']}: {response['error']['error_message']}")
                logger.error(log_msg)
                log_msg = (f"API Failed {info} with reason: {log_msg}")
                raise APICallFailedException(log_msg)
        return response
    
    def __setup_post_api_call(self, info, url, payload):
        success = 0
        for count in range(1, self.totalretries):
            try:
                response = self.__post_api_call(url=url, payload=payload)
            except ValueError as e:
                log_msg = (f"API to {info} failed attempt {count} of {self.totalretries} with {e}")
                print(log_msg)
                logger.warning(log_msg)
            except Exception as e:
                log_msg = (f"API to {info} failed with {e}")
                logger.error(log_msg)
                raise ValueError(log_msg)
            except:
                log_msg = (f"API to {info} failed attempt {count} of {self.totalretries} with unknown API error")
                print(log_msg)
                logger.warning(log_msg)
            else:
                success = 1
                break
        if success != 1:
            log_msg = (f"failed to {info}. Cannot continue.")
            log_msg += (" Check log file for details")
            logger.error(log_msg)
            raise APICallFailedException(log_msg)
        if 'error' in response:
            if response['error']['error_message']:
                log_msg = (f"Error Code {response['error']['error_id']}: {response['error']['error_message']}")
                logger.error(log_msg)
                log_msg = (f"API Failed {info} with reason: {log_msg}")
                raise APICallFailedException(log_msg)
        return response

    def __get_api_call(self, url):
        try:
            response = requests.get(url, headers= self.headers)
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err} - on API {url}')
            raise ValueError(f'HTTP error occurred: {http_err}') 
        if response is None:
            log_msg = "ERROR: No response received from XIQ!"
            logger.error(log_msg)
            raise ValueError(log_msg)
        if response.status_code != 200:
            log_msg = f"Error - HTTP Status Code: {str(response.status_code)}"
            logger.error(f"{log_msg}")
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.warning(f"\t\t{response.text}")
            else:
                if 'error_message' in data:
                    logger.warning(f"\t\t{data['error_message']}")
                else:
                    logger.warning(f"\n\n{data}")
            raise ValueError(log_msg) 
        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error(f"Unable to parse json data - {url} - HTTP Status Code: {str(response.status_code)}")
            raise ValueError("Unable to parse the data from json, script cannot proceed")
        return data
    
    def __put_api_call(self, url, payload):
        try:
            response = requests.put(url, headers= self.headers, data=payload)
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err} - on API {url}')
            raise ValueError(f'HTTP error occurred: {http_err}') 
        if response is None:
            log_msg = "ERROR: No response received from XIQ!"
            logger.error(log_msg)
            raise ValueError(log_msg)
        if response.status_code != 200:
            log_msg = f"Error - HTTP Status Code: {str(response.status_code)}"
            logger.error(f"{log_msg}")
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.warning(f"\t\t{response.text}")
            else:
                if 'error_message' in data:
                    logger.warning(f"\t\t{data['error_message']}")
                else:
                    logger.warning(f"{data}")
            raise ValueError(log_msg) 
        return "Success"

    def __post_api_call(self, url, payload):
        try:
            response = requests.post(url, headers= self.headers, data=payload)
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err} - on API {url}')
            raise ValueError(f'HTTP error occurred: {http_err}') 
        if response is None:
            log_msg = "ERROR: No response received from XIQ!"
            logger.error(log_msg)
            raise ValueError(log_msg)
        if response.status_code == 202:
            return response
        elif response.status_code != 200:
            log_msg = f"Error - HTTP Status Code: {str(response.status_code)}"
            logger.error(f"{log_msg}")
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.warning(f"\t\t{response.text()}")
            else:
                if 'error_message' in data:
                    logger.warning(f"\t\t{data['error_message']}")
                    raise Exception(data['error_message'])
            raise ValueError(log_msg)
        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error(f"Unable to parse json data - {url} - HTTP Status Code: {str(response.status_code)}")
            raise ValueError("Unable to parse the data from json, script cannot proceed")
        return data
      
    def __getAccessToken(self, user_name, password):
        info = "get XIQ token"
        success = 0
        url = self.URL + "/login"
        payload = json.dumps({"username": user_name, "password": password})
        for count in range(1, self.totalretries):
            try:
                data = self.__post_api_call(url=url,payload=payload)
            except ValueError as e:
                print(f"API to {info} failed attempt {count} of {self.totalretries} with {e}")
            except Exception as e:
                print(f"API to {info} failed with {e}")
                print('script is exiting...')
                raise SystemExit
            except:
                print(f"API to {info} failed attempt {count} of {self.totalretries} with unknown API error")
            else:
                success = 1
                break
        if success != 1:
            print("failed to get XIQ token. Cannot continue to import")
            print("exiting script...")
            raise SystemExit
        
        if "access_token" in data:
            #print("Logged in and Got access token: " + data["access_token"])
            self.headers["Authorization"] = "Bearer " + data["access_token"]
            return 0

        else:
            log_msg = "Unknown Error: Unable to gain access token for XIQ"
            logger.warning(log_msg)
            raise ValueError(log_msg)


    # PSK
    def change_PSK(self, ssid_id, psk):
        info = "to change psk"
        url = f"{self.URL}/ssids/{ssid_id}/psk/password"
        payload = psk
        try:
            response = self.__setup_put_api_call(info,url,payload)
        except APICallFailedException as e:
            response = "Failed"
        return response
    
    # LRO
    def __check_LRO(self, url):
        info = "to check LRO status"
        try:
            response = self.__setup_get_api_call(info,url)
        except APICallFailedException as e:
            raise APICallFailedException(e)
        return response['metadata']["status"]
        
    
    # Devices
    ## Check for config mismatches
    def collectMismatchDevices(self, pageSize=100, location_id=None, wait_time = 0):
        info = "to collect mismatch devices" 
        page = 1
        pageCount = 1
        firstCall = True
        if wait_time:
            print(f"Waiting {wait_time} seconds before checking for mismatched devices")
            time.sleep(wait_time)
        devices = []
        while page <= pageCount:
            url = self.URL + "/devices?views=FULL&page=" + str(page) + "&limit=" + str(pageSize) + "&connected=true&configMismatch=true"
            if location_id:
                url = url  + "&locationId=" +str(location_id)
            try:
                rawList = self.__setup_get_api_call(info,url)
            except APICallFailedException as e:
                raise APICallFailedException(e)
            devices = devices + rawList['data']

            if firstCall == True:
                pageCount = rawList['total_pages']
            print(f"completed page {page} of {rawList['total_pages']} collecting Devices")
            page = rawList['page'] + 1 
        return devices

    def configPushToDevices(self, device_id_list):
        info = "to push delta config update to devices"
        url = self.URL + "/deployments?async=true"
        payload = json.dumps({
        "devices": {
            "ids": 
            device_id_list
        },
        "policy": {
            "enable_complete_configuration_update": False,
            "firmware_upgrade_policy": {
            "enable_enforce_upgrade": False,
            "enable_distributed_upgrade": False
            },
            "firmware_activate_option": {
            "enable_activate_at_next_reboot": False,
            "activation_delay_seconds": 0,
            "activation_time": 0
            }
        }
        })
        try:
            response = self.__setup_post_api_call(info,url,payload)
        except APICallFailedException as e:
            raise APICallFailedException(e)
        # wait 60 seconds
        wait_time = 60
        print(f"waiting {wait_time} seconds for configuration push to start.")
        time.sleep(wait_time)
        #check LRO 
        try:
            lro_response = self.__check_LRO(response.headers['Location'])
        except APICallFailedException as e:
            raise APICallFailedException(e)
        return lro_response

