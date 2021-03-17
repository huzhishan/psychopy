#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2021 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from __future__ import absolute_import, print_function
from builtins import super  # provides Py3-style super() using python-future

from os import path
from pathlib import Path
from psychopy.experiment.components import BaseComponent, Param, _translate
from psychopy.localization import _localized as __localized
from psychopy.iohub.devices.eyetracker import eventTypes
_localized = __localized.copy()


class EyetrackerComponent(BaseComponent):
    """A class for using one of several eyetrackers to follow gaze"""
    categories = ['Responses']
    targets = ['PsychoPy']
    iconFile = Path(__file__).parent / 'eyetracker_record.png'
    tooltip = _translate('Eyetracker: use one of several eyetrackers to follow '
                         'gaze')

    def __init__(self, exp, parentName, name='eyes',
                 startType='time (s)', startVal=0.0,
                 stopType='duration (s)', stopVal=1.0,
                 startEstim='', durationEstim='',
                 events="", rois="",
                 #legacy
                 save='final', configFile='myTracker.yaml'):
        BaseComponent.__init__(self, exp, parentName, name=name,
                               startType=startType, startVal=startVal,
                               stopType=stopType, stopVal=stopVal,
                               startEstim=startEstim, durationEstim=durationEstim)
        self.type = 'Eyetracker'
        self.url = "https://www.psychopy.org/builder/components/eyetracker.html"
        self.exp.requirePsychopyLibs(['iohub', 'hardware'])
        # params
        self.order = ['config']  # first param after the name

        # useful params for the eyetracker - keep to a minimum if possible! ;-)
        self.params['events'] = Param(
            events, valType='list', inputType='multiChoice', categ='Basic',
            allowedVals=eventTypes,
            hint=_translate("What events should the eye tracker listen for?"),
            label=_translate("Event Types")
        )

        self.params['rois'] = Param(
            rois, valType='list', inputType='single', categ='Basic',
            hint=_translate("Regions of interest (ROIs) for the eyetracker, should be a list of component names. "
                            "To define an ROI without showing it, create a Polygon component with opacity set to 0."),
            label=_translate("ROIs")
        )

    def writePreWindowCode(self, buff):
        pass

    def writeInitCode(self, buff):
        inits = self.params
        code = (
            "%(name)s = eyetracker.EyeTrackerRecorder(win, eyetracker,\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                "events=%(events)s,\n"
                "rois=%(rois)s)\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)

    def writeRoutineStartCode(self, buff):
        """Write the code that will be called at the start of the routine
        """
        # create some lists to store recorded values positions and events if we
        # need more than one
        pass

    def writeFrameCode(self, buff):
        """Write the code that will be called every frame
        """
        inits = self.params
        buff.writeIndentedLines("# *%s* updates\n" % self.params['name'])

        # test for whether we're just starting to record
        # writes an if statement to determine whether to draw etc
        self.writeStartTestCode(buff)
        code = (
                "%(name)s.status = STARTED\n"
        )
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-1, relative=True)
        # Get rating each frame
        code = (
            "if %(name)s.status == STARTED:\n"
        )
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(1, relative=True)
        code = (
                "%(name)s.poll()\n"
        )
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-1, relative=True)

        # test for stop (only if there was some setting for duration or stop)
        if self.params['stopVal'].val not in ['', None, -1, 'None']:
            # writes an if statement to determine whether to draw etc
            self.writeStopTestCode(buff)
            code = ("%(name)s.status = FINISHED\n"
                    "%(name)s.setRecordingState(False)\n")
            buff.writeIndentedLines(code % self.params)
            # to get out of the if statement
            buff.setIndentLevel(-2, relative=True)

    def writeRoutineEndCode(self, buff):
        inits = self.params

        if len(self.exp.flow._loopList):
            inits['loop'] = self.exp.flow._loopList[-1].params['name']
            code = (
                 "%(loop)s.addData('%(name)s.x', list(%(name)s.data['x']))\n"
                 "%(loop)s.addData('%(name)s.y', list(%(name)s.data['y']))\n"
                 "%(loop)s.addData('%(name)s.roi', list(%(name)s.data['roi']))\n"
                 "%(loop)s.addData('%(name)s.pupil', list(%(name)s.data['pupil']))\n"
            )
            buff.writeIndentedLines(code % inits)
        super().writeRoutineEndCode(buff)

    def writeExperimentEndCode(self, buff):
        pass
