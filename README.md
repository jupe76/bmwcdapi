# bmwcdapi.py 
https://github.com/jupe76/bmwcdapi

Bmwcdapi.py is a python script to query various informations about your car from the BMW ConnectedDrive portal in conjunction with obenhab.

I'm using it for a BMW i3, but should work with other types as well.

The techniques to access the ConnectedDrive portal were taken from https://github.com/sergejmueller/battery.ebiene.de

### Prerequisites
You'll need the credentials (username / password) for a ConnectedDrive login and the 17 chars long vehicle ident number (VIN) of your car.
Furthermore you need a running openhab installation and python 3.x . The script has been tested with openhab2.

### Installation
Copy bmw.rules and bmw.items in the according openhab dirs.

Edit bmwUsername, bmwPassword and bmwVin placed in bmw.items to hold your credentials and the VIN of your car.

If your script dir is not /etc/openhab2/scripts than you need to edit bmw.rules.

Copy bmwcdapi.py to the openhab script dir. If the script is running on another computer than your openhab installation, than you need to adjust OPENHABIP.

Edit your sitemap to visualize the items.
The script is called every 2 hours to update the values. You can adjust the timespan in bmw.rules (be nice to the ConnectedDrive portal and don't hammer the server)
With the switch bmwForceUpdate you could initiate an immediate update.

### Roadmap
This is the first version of the script, it can only read values and has no support to initiate actions as to switch on heating or cooling.
Maybe I'll try to add this features later.
