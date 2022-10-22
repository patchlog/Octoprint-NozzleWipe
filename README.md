# OctoPrint-NozzleWipe
On long print jobs some types of plastic might accumulate on the nozzle and will eventually drip on the print which could, in the best case create lower qualify prints and in the worst case cause the print to completely fail.

This plugin will automatically wipe the nozzle every few minutes by pausing the print and moving the nozzle to a wipe area were you can "install" a wiping system. This could be as simple as a wire brush glued to the bed or something more complex like a motorised rotating brush.
After a few wiping moves the print is resumed.   

Inspired (and small parts copied) from https://github.com/cesarvandevelde/OctoPrint-M73Progress

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/patchlog/OctoPrint-NozzleWipe/archive/master.zip


## Configuration

The plugin will need the Settings -> Behaviour -> "Log position on pause" set 

The plugin behaviour can be tweaked with these configuration variables

* `Wipe position X`: X position where it will move the nozzle for wiping
* `Wipe position Y`: Y position where it will move the nozzle for wiping
* `Wipe position Z`: Z position where it will the nozzle for wiping
* `Wipe radius`: The nozzle will be moved randomly inside a circle with the center at (X,Y) and this radius
* `Wipe moves`: sets the number of moves to perform for wiping
* `Wipe interval`: Sets the number of minutes between wipes (default 7)
* `Retraction`: sets the number of millimeters to retract before wiping the nozzle
