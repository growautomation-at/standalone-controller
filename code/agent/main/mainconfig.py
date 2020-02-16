#!/usr/bin/python
# This file is part of Growautomation
#     Copyright (C) 2020  René Pascal Rath
#
#     Growautomation is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#     E-Mail: rene.rath@growautomation.at
#     Web: https://git.growautomation.at

#Growautomation General Configuration File
##### FORMAT is case-sensitive!!! #####

#############################  General  #############################

controller = "con01"

# Naming context
namemaxletters = 10
namemaxnumbers = 100

# DB
dbserver = "IP"
dbuser = "con01"
dbpassword = "PASSWORD"
sensordb = "sensors"
actiondb = "actions"


# Backup
backupenabled = "yes"   #yes/no -> If backup should be created
backuptime = "20:00"
backuplogs = "yes"      #yes/no -> If logs should be included into the backup

# Logs
loglevel = 0	        #2=debug/1=default/0=none
logactiontodb = "yes"   #yes/no -> If taken actions should be logged into the database


#############################  sensorS  #############################

#General Settings
sensortime = "10"		        #How often should the sensordata be written to the database (minutes)
sensorahtdisabled = "no"
sensorehdisabled = "no"

#Analog to Digital Converters
adcdisabled = ["adc02"]

#Which i2c bus the adc is connected to
adcconnected = {"adc01": "i2c-1", "adc02": "i2c-2"}


#Air Humidity Temperature
#ahta = Adafruit DHT22
ahtadisabled = ["ahta02"]

#Format:
#       {
#       "ahtaNR": "PIN",
#       "ahtaNR": "PIN"
#       }
ahtaconnected = {"ahta01": "26", "ahta02": "19"}

#Earth Humidity
#eha = generic analog china humidity sensor
#ehb = analog capacitive soil moisture sensor v1.2 (find on amazon)

#Format ["ehxNR", "ehxNR"]
ehbdisabled = ["ehb02"]

#Format:
#       {
#       "ehxNR": {
#           "AnalogToDigitalConverterNR": "adcpinNR"
#           },
#       "ehxNR": {
#           "adcNR": "adcpinNR"
#           }
#       }
ehbconnected = {"ehb01": {"adc01": "0"}, "ehb02": {"adc02": "1"}}


############################# CHECKS #############################

#How many sensor data records should be checked to determine if an action should be taken
checkrange = 6
#row containing the sensor data	-> counted from left without counting the ID row
checkdbdatacolumn = 4


#############################  actions  #############################

#actiontypes
#Which action should react to which sensortype
actiontypes = {"eh": ("pump", "win"), "aht": ("win")}


#actionblocks
#Links sensors and actions -> simplifies configuration and processing
#Format:
#       {
#       "sensorS": {
#           "eh": ("*"),
#           "aht": ("*")
#           },
#       "actions": {
#           "pump": ("*"),
#           "win": ("*")
#           }
#       }
actionblock01 = {"sensors": {"eh": ("ehb01", "ehb02"), "aht": ("ahta01", "ahta02")}, "actions": {"win": ("wina02")}}
actionblock02 = {"sensors": {"eh": ("ehb01", "ehb02")}, "actions": {"pump": ("pumpa01", "pumpa04"), "win": ("wina01")}}


#Water pumps
#Generic water pumps -> are controlled via network attached power strip
pumpdisabled = []

#Format:
#       (
#       "pumpxNR",
#       "pumpxNR"
#       )

pumpconnected = ("pumpa01", "pumpa04")

pumpactivation = "60"		#The pump will be activated if the humidity falls under this value
pumptime = 10 #600		    #Runtime in seconds

#window-Openers
#12V DC motors with 3d-printed window-opener attachments
#DC motor driver L298N Dual-H-Bridge
windisabled = {}

#Format:
#       {
#       "winNR": {
#           "FWD": "PINForward",
#           "REV": "PINReverse"
#           },
#       "winNR": {
#           "FWD": "PINForward,
#           "REV": "PINReverse"
#           }
#       }
winconnected = {"win01": {"fwd": "20", "rev": "21"}, "win02": {"fwd": "16", "rev": "12"}}
winopentime = 5

#Power Strips
#psua: Gembird Energenie EG-PMS2-LAN (trashy hard- and firmware) -> would not recommend buying it

psua01password = "PASSWORD"
psua01ip = "IP"
psua01webport = 8080

#Format:
#       {
#       "outletNR": "actionobjectxNR",
#       "outletNR": "actionobjectxNR"
#       }
psua01outlets = {"1": "pumpa01", "2": "pumpa02", "3": "pumpa03", "4": ""}
psua02password = "PASSWORD"
psua02ip = "IP"
psua02webport = 8080
psua02outlets = {"1": "pumpa04", "2": "", "3": "", "4": ""}

#psub: Coming soon (: