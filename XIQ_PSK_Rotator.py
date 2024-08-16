#!/usr/bin/env python3

###########################################################################
# written by:   Tim Smith
# e-mail:       tismith@extremenetworks.com
# date:         16 Aug 2024
# version:      1.0.0
#
# Note: The script is not officially supported by Extreme Networks
#
###########################################################################

import logging
import os
import csv
import yaml
from app.logger import logger
from app.xiq_api import XIQ
import app.gmail as gmail_client
import app.smtp as smtp_client
from pprint import pprint as pp
logger = logging.getLogger('PSK_Rotator.Main')

PATH = os.path.dirname(os.path.abspath(__file__))

 # search for variables.yml
try:
    with open(f"{PATH}/variables.yml", "r") as f:
        yml_variables = yaml.safe_load(f)
except FileNotFoundError:
    logger.error("variables.yml file not found")
    raise SystemExit
except yaml.YAMLError:
    logger.error("variables.yml file is corrupt")
    raise SystemExit


# CSV Functions
#################################################################################################
def write_to_csv(data, output_file):
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

# Email Functions
#################################################################################################
def send_email(isSuccess, msg):
    if yml_variables['email_type'] == 'gmail':
        send_gmail(msg)
    elif yml_variables['email_type'] == 'smtp':
        send_smtp(msg)
    elif yml_variables['email_type'] == 'disabled':
        print("emailing is disabled in yaml variable file. Message will only be logged.")
        logger.info(f"Script was successful: {isSuccess}")
        logger.info(f"Email is disabled. Email message: {msg}")
    else:
        print(f"email_type in variables.yml is incorrect - '{yml_variables['email_type']}' .")
        logger.info(f"Script was successful: {isSuccess}")
        logger.info(f"email_type in variable.yml is incorrect - '{yml_variables['email_type']}'. Email message: {msg}")

def send_gmail(msg):
    # open gmail_client
    service = gmail_client.new(yml_variables)
    service.send_message(body=(f"{msg}"))

def send_smtp(msg):
    service = smtp_client.new(yml_variables)
    service.send_message(body=(f"{msg}"))
    
#################################################################################################
# Main
#################################################################################################

if 'XIQ_token' in yml_variables:
    x = XIQ(token=yml_variables['XIQ_token'])
else:
    print("No XIQ API token provided. Please generate a token and run the script again.")
    raise SystemExit


# read csv file
if os.path.exists(yml_variables['file_name']):
    with open(yml_variables['file_name'], 'r') as csv_f:
        reader = csv.reader(csv_f)
        psk_list = list(reader)
else:
    log_msg = f"File {yml_variables['file_name']} does not exist."
    logger.error(log_msg)
    print("Failed")
    print(log_msg)
    raise SystemExit     

if not psk_list:
    log_msg = (f"The PSK CSV file {yml_variables['file_name']} is empty")
    logger.warning(log_msg)
    print(log_msg)
    send_email(False, log_msg)
    print("Script is exiting...")
    raise SystemExit

# Check for any devices in mismatched state. 
mismatched_devices = x.collectMismatchDevices()
if len(mismatched_devices) > 0 and not yml_variables['allow_mismatched']:
    #Do this is mismatched devices and allow_mismatched is set to False
    log_msg = f"Mismatches devices were found in XIQ. Yaml settings are set to not allow mismatches. PSK will not be changed"
    logger.warning(log_msg)
    log_msg += f"\n\nThe following APs are in a mismatched state: \n{'chr(10)'.join([d['hostname'] for d in mismatched_devices])}"
    send_email(False, log_msg)
    print("Script is exiting...")
    raise SystemExit
        

email_body = ''

new_psk = psk_list.pop(0)[0]

psk_updated = False
response = x.change_PSK(yml_variables['SSID_ID'],new_psk)
if response == "Success":
    psk_updated = True
    logger.info(f"Successfully updated psk to {new_psk}")
    #update csv 
    write_to_csv(psk_list, yml_variables['file_name'])
    logger.info(f"Successfully updated csv file {yml_variables['file_name']}")
    email_body += f"{yml_variables['email_msg']} {new_psk}\n\n"
else:
    email_body += f"Script failed to change PSK. Please check logs\n\n"

config_status_msg = ""
if yml_variables['allow_config_push'] and psk_updated:
    devices = x.collectDevices()
    config_status = x.configPushToDevices([device['id'] for device in devices])
    if config_status != "SUCCEEDED":
        if config_status[-2:] == 'ED' :
            config_status_msg = f"The configuration push {config_status}"
        else:
            config_status_msg = f"The cofiguration push is {config_status}"
elif not yml_variables['allow_config_push'] and psk_updated:
    config_status_msg = 'Configuration pushing is disabled in script. New PSK will be used once configuration is pushed.'

email_body += config_status_msg
send_email(True, email_body)