#!/usr/bin/env python
# referenciado nesse site
# https://github.com/brendan-myers/rpi3-wifi-conf
# https://github.com/brendan-myers/rpi3-wifi-conf-android

import os
from bluetooth import *
from wifi import Cell, Scheme
import subprocess
import time

wpa_supplicant_conf = "/etc/wpa_supplicant/wpa_supplicant.conf"
sudo_mode = "sudo "


## Programm to connect via Bluetooth to an Android Cellphone and configure Wi-Fi
## run by line command 'sudo python3 connect-wifi-via-bluetoooth.py'

def wifi_connect(ssid, psk):
    
    # write wifi config to file
    f = open('wifi.conf', 'w')
    f.write('country=BR\n')
    f.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
    f.write('update_config=1\n')
    f.write('\n')
    f.write('network={\n')
    f.write('    ssid="' + str(ssid)[2:-1] + '"\n')
    f.write('    psk="' + str(psk)[2:-1] + '"\n')
    f.write('}\n')
    f.close()

    cmd = 'sudo mv wifi.conf ' + wpa_supplicant_conf
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

    cmd = 'ifconfig wlan0'
    cmd_result = os.system(cmd)
    print (cmd + " - " + str(cmd_result))
    

    p = subprocess.Popen(['ifconfig', 'wlan0'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    out, err = p.communicate()
    
    ip_address = "<Not Set>"
    
    for l in out.split(b'\n'):
        if l.strip().startswith(b'inet '):
            ip_address = l[13:27]

    return ip_address


def ssid_discovered():
    
    aps = Cell.all('wlan0')
    aps_info = []
    for current in aps:
        aps_info.append(current.ssid)

    wifi_info = 'Found ssid : \n'

    for current in range(len(aps_info)):
        wifi_info +=  aps_info[current] + "\n"


    wifi_info+="!"

    print (wifi_info)
    return wifi_info


def handle_client(client_sock) :
    # get ssid
    client_sock.send(ssid_discovered())
    print ("Waiting for SSID...")

    ssid = client_sock.recv(1024)
    if ssid == '' :
        return

    print ("ssid received")
    print (ssid)

    # get psk
    client_sock.send("waiting-psk!")
    print ("Waiting for PSK...")

    psk = client_sock.recv(1024)
    if psk == '' :
        return

    print ("psk received")
    print (psk)

    ip_address = wifi_connect(ssid, psk)
    
    ip = 'ip address:' + str(ip_address)[2:-1]    
    print(ip)
    
    client_sock.send("Connected-to-Wi-Fi!")
       
    return

def connectByBluetooth():
    # need to Run APK file into cellphone before connecting

        
    cmd = 'sudo hciconfig hci0 piscan'
    cmd_result = os.system(cmd)
        
    cmd = 'sudo sdptool add --channel=22 SP'
    cmd_result = os.system(cmd)
        
    server_sock = BluetoothSocket(RFCOMM)
    server_sock.bind(("",PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    uuid = "815425a5-bfac-47bf-9321-c5ff980b5e11"

    advertise_service( server_sock, "RPi Wifi config",
                        service_id = uuid,
                        service_classes = [ uuid, SERIAL_PORT_CLASS ],
                        profiles = [ SERIAL_PORT_PROFILE ])


    print ('Waiting for connection on RFCOMM channel {}'.format(port))

    client_sock, client_info = server_sock.accept()
    print ('Accepted connection from {}'.format(client_info))

    handle_client(client_sock)
        
    client_sock.close()
    server_sock.close()

    # finished config
    print ("finished configuration")
        

if __name__ == "__main__":

    try:
        hostname = "google.com"
        response = os.system("ping -c 1 " + hostname)
        
        if response == 0:
            pingstatus = "Network Active"
            print(pingstatus)
        else:
            pingstatus = "Network Error"
            print(pingstatus + ' - Connecting using Bluetooth channel')
            connectByBluetooth()

    except (KeyboardInterrupt, SystemExit):
        print('\nExiting\n')
        
