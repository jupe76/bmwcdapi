#! /usr/bin/env python3
# 
# **** bmwcdapi.py ****
# https://github.com/jupe76/bmwcdapi
#
# Query vehicle data from the BMW ConnectedDrive Website, i.e. for BMW i3
# Based on the excellent work by Sergej Mueller
# https://github.com/sergejmueller/battery.ebiene.de
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import json
import requests
import time
import urllib.parse
import re
import argparse

# ADJUST HERE if OH is not running on "localhost:8080"
OPENHABIP = "localhost:8080"

# API Gateway
AUTH_API = 'https://customer.bmwgroup.com/gcdm/oauth/authenticate'
VEHICLE_API = 'https://www.bmw-connecteddrive.de/api/vehicle'

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"

class ConnectedDrive(object):

    def __init__(self):
        self.printval = False
        self.bmwUsername = self.ohGetValue("bmwUsername").json()["label"]
        self.bmwPassword = self.ohGetValue("bmwPassword").json()["label"]
        self.bmwVin = self.ohGetValue('bmwVin').json()["label"].upper()
        self.accessToken = self.ohGetValue('accessToken').json()["state"]
        self.tokenExpires = self.ohGetValue('tokenExpires').json()["state"]

        if((self.tokenExpires == 'NULL') or (int(time.time()) >= int(self.tokenExpires))):
            self.generateCredentials()

    def generateCredentials(self):
        """
        If previous token has expired, create a new one.
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-agent": USER_AGENT
        }

        values = {'username' : self.bmwUsername,
            'password' : self.bmwPassword,
            'client_id' : 'dbf0a542-ebd1-4ff0-a9a7-55172fbfce35',
            'redirect_uri' : 'https://www.bmw-connecteddrive.com/app/default/static/external-dispatch.html',
            'response_type' : 'token',
            'scope' : 'authenticate_user fupo',
            'state' : 'eyJtYXJrZXQiOiJkZSIsImxhbmd1YWdlIjoiZGUiLCJkZXN0aW5hdGlvbiI6ImxhbmRpbmdQYWdlIn0',
            'locale' : 'DE-de'
        }

        data = urllib.parse.urlencode(values)
        r = requests.post(AUTH_API,  data=data, headers=headers,allow_redirects=False)
        #statuscode will be 302
        #print(r.status_code)

        myPayLoad=r.headers['Location']
        m = re.match(".*access_token=([\w\d]+).*token_type=(\w+).*expires_in=(\d+).*", myPayLoad )
        
        tokenType=(m.group(2))

        self.accessToken=(m.group(1))
        self.ohPutValue('accessToken',self.accessToken)

        self.tokenExpires=int(time.time()) + int(m.group(3))
        self.ohPutValue('tokenExpires',self.tokenExpires)

    def ohPutValue(self, item, value):
        rc =requests.put('http://' + OPENHABIP + '/rest/items/'+ item +'/state', str(value))
        if(rc.status_code != 202):
            print("Warning: couldn't save item " + item + " to openHAB")

    def ohGetValue(self, item):
        return requests.get('http://' + OPENHABIP + '/rest/items/'+ item)

    def call(self):
        headers = {
            "Content-Type": "application/json",
            "User-agent": USER_AGENT,
            "Authorization" : "Bearer "+ self.accessToken
            }
        r = requests.get(VEHICLE_API+'/dynamic/v1/'+self.bmwVin+'?offset=-60', headers=headers,allow_redirects=True)

        map=r.json() ['attributesMap']
        #optional print all values
        if(self.printval==True):
            for k, v in map.items():
                print(k, v)
        
        if('door_lock_state' in map):
            self.ohPutValue("doorLockState",map['door_lock_state'])
        if('chargingLevelHv' in map):
            self.ohPutValue("chargingLevelHv",map['chargingLevelHv'])
        if('beRemainingRangeElectric' in map):
            self.ohPutValue("beRemainingRangeElectric",map["beRemainingRangeElectric"])
        if('mileage' in map):
            self.ohPutValue("mileage",map["mileage"])
        if('beRemainingRangeFuel' in map):
            self.ohPutValue("beRemainingRangeFuel",map["beRemainingRangeFuel"])
        if('updateTime_converted_date' in map):
            self.ohPutValue("updateTimeConverted", map['updateTime_converted_date']+ " " + map['updateTime_converted_time'])
        if('chargingSystemStatus' in map):
            self.ohPutValue("chargingSystemStatus", map['chargingSystemStatus'])
        if('remaining_fuel' in map):
            self.ohPutValue("remainingFuel", map['remaining_fuel'])

        r = requests.get(VEHICLE_API+'/navigation/v1/'+self.bmwVin, headers=headers,allow_redirects=True)
        map=r.json()

        #optional print all values
        if(self.printval==True):
            for k, v in map.items():
                print(k, v)

        if('socMax' in map):
            self.ohPutValue("socMax",map['socMax'])

        r = requests.get(VEHICLE_API+'/efficiency/v1/'+self.bmwVin, headers=headers,allow_redirects=True)

        if(self.printval==True):
            for k, v in r.json().items():
                print(k, v)

        #lastTripList
        myList=r.json() ["lastTripList"]
        for listItem in myList:
            if (listItem["name"] == "LASTTRIP_DELTA_KM"):
                pass
            elif (listItem["name"] == "ACTUAL_DISTANCE_WITHOUT_CHARGING"):
                pass
            elif (listItem["name"] == "AVERAGE_ELECTRIC_CONSUMPTION"):
                self.ohPutValue("lastTripAvgConsum", listItem["lastTrip"])
            elif (listItem["name"] == "AVERAGE_RECUPERATED_ENERGY_PER_100_KM"):
                self.ohPutValue("lastTripAvgRecup", listItem["lastTrip"])
            elif (listItem["name"] == "CUMULATED_ELECTRIC_DRIVEN_DISTANCE"):
                pass

def main():
    print("...running bmwcdapi.py")
    c = ConnectedDrive()

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--printval', action='store_true', help='print all values that were received')
    args = vars(parser.parse_args())

    if(args["printval"]==True):
        c.printval=True

    c.call()

if __name__ == '__main__':
    main()
