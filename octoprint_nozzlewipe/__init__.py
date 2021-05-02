# coding=utf-8
from __future__ import absolute_import, division

import logging

import octoprint.plugin
from octoprint.events import Events
from octoprint.printer import PrinterCallback
from flask_babel import gettext
import random


logger = logging.getLogger(__name__)


class ProgressMonitor(PrinterCallback):
    def __init__(self, plugin, *args, **kwargs):
        super(ProgressMonitor, self).__init__(*args, **kwargs)
        self.reset()
        logger.info("ARGS")
        logger.info(args)
        self.plugin=plugin
        self.job_hold=False
    def reset(self):
        self.completion = None
        self.time_elapsed_s = None
        self.time_left_s = None

    def on_printer_send_current_data(self, data):
        logger.info("on_printer_send_current_data");
        logger.info(data);
        self.completion = data["progress"]["completion"]
        self.time_elapsed_s = data["progress"]["printTime"]
        self.time_left_s = data["progress"]["printTimeLeft"]
        if self.time_elapsed_s!=None and self.time_elapsed_s/60>=self.plugin.next_wipe and self.job_hold==False:
            if self.plugin._printer.set_job_on_hold(True):
                self.job_hold=True
                self.plugin._printer.commands("M114")


class NozzleWipePlugin(
    octoprint.plugin.ProgressPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.RestartNeedingPlugin
):
    def on_after_startup(self):
        self._progress = ProgressMonitor(self)
        self._printer.register_callback(self._progress)

        self.wipe_interval=3;

        settings = self._settings
        self.wipe_interval = settings.get_int(["wipe_interval"])
        self.wipe_position_x = settings.get_float(["wipe_position_x"])
        self.wipe_position_y = settings.get_float(["wipe_position_y"])
        self.wipe_position_z = settings.get_float(["wipe_position_z"])
        self.wipe_radius = settings.get_float(["wipe_radius"])
        self.wipe_moves = settings.get_int(["wipe_moves"])
        self.retraction = settings.get_float(["retraction"])

        if(self.wipe_interval<1):
            self.wipe_interval=1;
        self.next_wipe=self.wipe_interval;


    def on_event(self, event, payload):
        self._logger.info("IN EVENT")
        self._logger.info(event)
        self._logger.info(payload)

        if event == Events.PRINT_STARTED or event == Events.PRINT_DONE:
            # Firmware manages progress bar when printing from SD card
            if payload.get("origin", "") == "sdcard":
                return

        if event == Events.PRINT_STARTED:
            self._progress.reset()
            self.next_wipe=self.wipe_interval

        if event == Events.POSITION_UPDATE and self._progress.time_elapsed_s!=None and self._progress.time_elapsed_s/60>=self.next_wipe:
            if not (self.next_wipe<=self.wipe_interval and payload["z"]>1):
                self._last=payload
                self._wipe()
                self._resume()
            self._printer.set_job_on_hold(False)
            self.next_wipe = self._progress.time_elapsed_s/60 + self.wipe_interval;
            self._progress.job_hold=False

    def _resume(self):
        # absolute XYZ
        self._printer.commands("G90")

        if self._last["z"]<self.wipe_position_z:
            self._printer.commands("G1 Z{} F4500".format(self.wipe_position_z))
        else:
            self._printer.commands("G1 Z{} F4500".format(self._last["z"]))

        # move back to pause position XY
        self._printer.commands("G1 X{} Y{} Z{} F4500".format(self._last["x"],self._last["y"], self._last["z"]))

        # set relative extruder
        self._printer.commands("M83")
        # prime nozzle
        self._printer.commands("G1 E+5 F4500")

        # absolute E
        self._printer.commands("M82")

        # reset E
        self._printer.commands("G92 E{}".format(self._last["e"]))

        #reset to feed rate before pause if available
        if self._last["f"] != None:
            self._printer.commands("G1 F{}".format(self._last["f"]))

    def _wipe(self):
        # set relative
        self._printer.commands("G91")
        self._printer.commands("M83")
        #retract filament
        self._printer.commands("G1 Z+1 E-5 F4500")
        # absolute
        self._printer.commands("G90")
        self._printer.commands("M82")
        if self._last["z"]<self.wipe_position_z:
            self._printer.commands("G1 Z{}".format(self.wipe_position_z))

        # move to the wiper's XY position
        gcode="G1 X{} Y{}".format(self.wipe_position_x,self.wipe_position_y)
        self._printer.commands(gcode)

        gcode=gcode="G1 Z{}".format(self.wipe_position_z)
        self._printer.commands(gcode)

        for m in range(self.wipe_moves-1):
            gcode="G1 X{} Y{}".format(self.wipe_position_x+random.randint(0-self.wipe_radius,self.wipe_radius),self.wipe_position_y+random.randint(0-self.wipe_radius,self.wipe_radius))
            self._printer.commands(gcode)


    def get_settings_defaults(self):
        return dict(
            wipe_position_x=100,
            wipe_position_y=100,
            wipe_position_z=19.5,
            wipe_radius=7,
            wipe_moves=10,
            retraction=5,
            wipe_interval=7
        )

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        settings = self._settings
        self.wipe_position_x = settings.get_float(["wipe_position_x"])
        self.wipe_position_y = settings.get_float(["wipe_position_y"])
        self.wipe_position_z = settings.get_float(["wipe_position_z"])
        self.wipe_radius = settings.get_float(["wipe_radius"])
        self.wipe_moves = settings.get_int(["wipe_moves"])
        self.retraction = settings.get_float(["retraction"])
        self.wipe_interval = settings.get_int(["wipe_interval"])

        if self.wipe_moves<2:
            self.wipe_moves=2

        if self.retraction<1:
            self.retraction=1

        if self.wipe_radius<3:
            self.wipe_radius=3

        if(self.wipe_interval<1):
            self.wipe_interval=1;

        self.next_wipe=self.wipe_interval;


    def get_template_configs(self):
        return [
            dict(
                type="settings",
                name=gettext("Nozzle wipe"),
                custom_bindings=False
            )
        ]

    def get_update_information(self):
        return dict(
            nozzlewipe=dict(
                displayName="Nozzle Wipe",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="patchlog",
                repo="OctoPrint-NozzleWipe",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/patchlog/OctoPrint-NozzleWipe/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "Nozzle Wipe Plugin"
__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = NozzleWipePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config":
            __plugin_implementation__.get_update_information
    }
