# bmwcdapi.py 
https://github.com/jupe76/bmwcdapi

Bmwcdapi.py is a python script to query various informations about your car from the BMW ConnectedDrive portal 
in conjunction with obenhab.

I'm using it for a BMW i3, but should work with other types as well.

The techniques to access the ConnectedDrive portal were taken from https://github.com/sergejmueller/battery.ebiene.de

### Prerequisites
You'll need the credentials (username / password) for a ConnectedDrive login and the 17 chars long vehicle ident number (VIN) 
of your car.
Furthermore you need a running openhab installation and python 3.x . The script has been tested with openhab2.

### Installation
Copy bmw.rules and bmw.items in the according openhab dirs.

Edit Bmw_Username, Bmw_Password and Bmw_Vin placed in bmw.items to hold your credentials and the VIN of your car.

If your script dir is not /etc/openhab2/scripts than you need to edit bmw.rules.

Copy bmwcdapi.py to the openhab script dir. If the script is running on another computer than your openhab installation, 
than you need to adjust OPENHABIP.

Edit your sitemap to visualize the items.

### Usage
The script is called every 30 min to update the values. You can adjust the timespan in bmw.rules (be nice to the 
ConnectedDrive portal and don't hammer the server)
With the switch Bmw_ForceUpdate you could initiate an immediate update.

To execute services like to climate the car, call the bmwcd api.py with the commandline parameter --execservice 
and the appropriate service, i.e. bmwcdapi.py --execservice climate

### Supported Items

| OH-Item                       | Type   | Description                        |
| ----------------------------- | ------ |------------------------------------|
|`Bmw_Username`                 | String | BMW ConnectedDrive username        |
|`Bmw_Password`                 | String | BMW ConnectedDrive password        |
|`Bmw_Vin`                      | String | 17 chars long VIN of the car       |
|`Bmw_Climate`                  | Switch | Switch to call the service to climate the car |
|`Bmw_LockDoors`                | Switch | Switch to lock the car             |
|`Bmw_UnlockDoors`              | Switch | Switch to unlock the car           |
|`Bmw_ForceUpdate`              | Switch | switch to update the values immediately|
|`Bmw_accessToken`              | String | access token                       |
|`Bmw_tokenExpires`             | String | Timestamp at which the accesstoken becomes invalid |
|`Bmw_doorLockState`            | String | state of the door locks            |
|`Bmw_socMax`                   | Number | maximum "state of charge" in kWh   |
|`Bmw_chargingLevelHv`          | Number | charging level in percent          |
|`Bmw_beRemainingRangeElectric` | Number | remaining electric range in km     |
|`Bmw_beRemainingRangeFuel`     | Number | remaining fuel range in km         |
|`Bmw_mileage`                  | Number | mileage                            |
|`Bmw_chargingSystemStatus`     | String | charging state                     |
|`Bmw_updateTimeConverted`      | String | last status update from the car    |
|`Bmw_remainingFuel`            | Number | remaining fuel in l                |
|`Bmw_lastTripAvgConsum`        | Number | average consum of last trip in kWh |
|`Bmw_lastTripAvgRecup`         | Number | average recuperation of last trip in kWh| 

### Commandline parameters
If bmwcdapi.py is called without parameters, the current values will be queried from ConnectedDrive and propagated to openHAB.

| parameter long         | parameter short | Description                                                 |
| ---------------------- | ----------------|-------------------------------------------------------------|
|--help                  | -h              | show commandline help                                       |
|--printall              | -p              | print all values, usefull for debuging or just for exploring|
|--execservice <service> | -e              | execute service service may be one of <ul><li>climate,</li><li>lock,</li><li>unlock,</li><li>light,</li><li>horn|</li></ul>|
|--sendmesg <subject> <message>| -s              | send a message to the car             | 

### Return codes

| return code  | Description                        |
| ------------ | -----------------------------------|
|`0`           |OK                                  |
|`13`          | EACCES Permission denied           |
|`62`          | ETIME, Timeout                     |
|`70`          | ECOMM, Communication error         |
