""" Class used to create and control radamec device """
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from direct.task.TaskManagerGlobal import taskMgr
from .DirectDeviceManager import DirectDeviceManager

from direct.directnotify import DirectNotifyGlobal

#TODO: Handle interaction between widget, followSelectedTask and updateTask

# ANALOGS
RAD_PAN = 0
RAD_TILT = 1
RAD_ZOOM = 2
RAD_FOCUS = 3

class DirectRadamec(DirectObject):
    radamecCount = 0
    notify = DirectNotifyGlobal.directNotify.newCategory('DirectRadamec')

    def __init__(self, device = 'Analog0', nodePath = None):
        # See if device manager has been initialized
        if base.direct.deviceManager is None:
            base.direct.deviceManager = DirectDeviceManager()
        # Set name
        self.name = f'Radamec-{repr(DirectRadamec.radamecCount)}'
        DirectRadamec.radamecCount += 1
        # Get analogs
        self.device = device
        self.analogs = base.direct.deviceManager.createAnalogs(self.device)
        self.numAnalogs = len(self.analogs)
        self.aList = [0, 0, 0, 0, 0, 0, 0, 0]
        # Radamec device max/mins
        # Note:  These values change quite often, i.e. everytime
        #        you unplug the radamec cords, or jostle them too
        #        much.  For best results, re-record these values often.
        self.minRange = [-180.0, -90, 522517.0, 494762.0]
        self.maxRange = [180.0, 90, 547074.0, 533984.0]
        # Spawn update task
        self.enable()

    def enable(self):
        # Kill existing task
        self.disable()
        # Update task
        taskMgr.add(self.updateTask, f'{self.name}-updateTask')

    def disable(self):
        taskMgr.remove(f'{self.name}-updateTask')

    def destroy(self):
        self.disable()

    def updateTask(self, state):
        # Update analogs
        for i in range(len(self.analogs)):
            self.aList[i] = self.analogs.getControlState(i)
        return Task.cont

    def radamecDebug(self):
        panVal = self.normalizeChannel(RAD_PAN, -180, 180)
        tiltVal = self.normalizeChannel(RAD_TILT, -90, 90)

        self.notify.debug(f"PAN = {self.aList[RAD_PAN]}")
        self.notify.debug(f"TILT = {self.aList[RAD_TILT]}")
        self.notify.debug(f"ZOOM = {self.aList[RAD_ZOOM]}")
        self.notify.debug(f"FOCUS = {self.aList[RAD_FOCUS]}")
        self.notify.debug(f"Normalized: panVal: {panVal}  tiltVal: {tiltVal}")

    # Normalize to the range [-minVal, maxVal] based on some hard-coded
    # max/min numbers of the Radamec device
    def normalizeChannel(self, chan, minVal = -1, maxVal = 1):
        if chan < 0 or chan >= min(len(self.maxRange), len(self.minRange)):
            raise RuntimeError("can't normalize this channel (channel %d)" % chan)

        maxRange = self.maxRange[chan]
        minRange = self.minRange[chan]

        diff = maxRange - minRange
        clampedVal = max(min(self.aList[chan], maxRange), maxRange)
        return ((maxVal - minVal) * (clampedVal - minRange) / diff) + minVal
