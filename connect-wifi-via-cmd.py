#!/usr/bin/env python

import os
from bluetooth import *
from wifi import Cell, Scheme
import subprocess
import time

wpa_supplicant_conf = "/etc/wpa_supplicant/wpa_supplicant.conf"
sudo_mode = "sudo "


def wifi_connect(ssid, psk):
    
    # write wifi config to file
    # if delete -a option in tee command, erase all file before write it
    cmd = 'sudo wpa_passphrase "{}" "{}" | sudo tee -a {conf} > /dev/null'.format(ssid,psk,conf=wpa_supplicant_conf)
    cmd_result = ""
    cmd_result = os.system(cmd)
    print (cmd + " - " + str(cmd_result))

    # reconfigure wifi
    cmd = sudo_mode + 'wpa_cli -i wlan0 reconfigure'
    cmd_result = os.system(cmd)
    print (cmd + " - " + str(cmd_result))

    time.sleep(10)

    cmd = 'iwconfig wlan0'
    cmd_result = os.system(cmd)
    print (cmd + " - " + str(cmd_result))
    
def ssid_discovered():
    
    aps = Cell.all('wlan0')
    wifi_info = []
    for current in aps:
        wifi_info.append(current.ssid)
    return wifi_info

def addWifi(SSID, password):
    
  config_lines = [
    '\n',
    'network={',
    '\tssid="{}"'.format(SSID),
    '\tpsk="{}"'.format(password),
    '\tkey_mgmt=WPA-PSK',
    '}'
  ]

  config = '\n'.join(config_lines)
  print(config)

  with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a+") as wifi:
    wifi.write(config)

  print("Wifi config added")
  
def reconfigureWifi():
    
    # reconfigure wifi
    cmd = sudo_mode + 'wpa_cli -i wlan0 reconfigure'
    cmd_result = os.system(cmd)
    print (cmd + " - " + str(cmd_result))
    time.sleep(10)
    
def connectByCMD():
                   
    ap = []
    ap = ssid_discovered()
    print ('SSID disponiveis:')
    print (ap)
    
    print('Escolha uma rede e entre com o SSID e a senha')
    ssid = input('Enter SSID: ')
    psw = input('Enter password: ')    
    #addWifi(ssid,psw)
    #reconfigureWifi()
    wifi_connect(ssid,psw)

try:
    connectByCMD()
      
except (KeyboardInterrupt, SystemExit):
    print ('\nExiting\n')