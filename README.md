# OctoPrint-NozzleWipe
On long print jobs plastic will accumulate on the nozzle and will eventually drip on the print which could in the best case create lower qualify prints and in the worst case cause the print to completely fail.

This plugin will automatically wipe the nozzle every few minutes by pausing the print, moving the nozzle to a wipe area were you can "install" a wiping system. This could be as simple as a wire brush glued to the bed or something more complex like a motorised rotating brush   

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/patchlog/OctoPrint-NozzleWipe/archive/master.zip


## Configuration

The plugin will need the Settings -> Behaviour -> Log position on pause set and some pause / resume scripts setup


After printjob is paused:
  {% if pause_position.x is not none %}
  ; relative XYZE
  G91
  M83

  ; retract filament, move Z slightly upwards
  G1 Z+5 E-5 F4500

  ; absolute XYZE
  M82
  G90

  ; move to a safe rest position, adjust as necessary
  G1 X0 Y0
  {% endif %}

After printjob is resumed:
  {% if pause_position.x is not none %}
  ; relative extruder
  M83

  ; prime nozzle
  G1 E-5 F4500
  G1 E5 F4500
  G1 E5 F4500

  ; absolute E
  M82

  ; absolute XYZ
  G90

  ; reset E
  G92 E{{ pause_position.e }}

  ; move back to pause position XYZ
  G1 X{{ pause_position.x }} Y{{ pause_position.y }} Z{{ pause_position.z }} F4500

  ; reset to feed rate before pause if available
  {% if pause_position.f is not none %}G1 F{{ pause_position.f }}{% endif %}
  {% endif %}

There are 4 options to fine-tune the plugin's behavior, available through the `Nozzle Wipe` tab in OctoPrint
settings.

* `Wipe position X`: The X position where to move the nozzle for wiping
* `Wipe position Y`: The Y position where to move the nozzle for wiping
* `Wipe position Z`: The Z position where to move the nozzle for wiping

* `Use time estimate`: By default, the plugin uses OctoPrint's built-in progress
  estimate, which is based on the progress inside a G-code file. In some cases,
  a better progress estimate can be calculated from the time elapsed and the
  time remaining: `P = elapsed / (elapsed + remaining)`.
