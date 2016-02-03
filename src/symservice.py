from os.path import splitext, abspath
from sys import modules

import os
import sys
import win32serviceutil
import win32service
import win32event
import win32api
import ctypes

class Service(win32serviceutil.ServiceFramework):
    _svc_name_ = '_SymlinkService'
    _svc_display_name_ = '_SymlinkCreator'
    __CSL = None

    def __init__(self, *args):
        win32serviceutil.ServiceFramework.__init__(self, *args)
        self.log('init')
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def log(self, msg):
        import servicemanager
        servicemanager.LogInfoMsg(str(msg))

    def sleep(self, sec):
        win32api.Sleep(sec*1000, True)
    """
    def symlink(self, source, target):
        path = os.path.dirname(source)
        file_name = os.path.basename(source)
        os.chdir(path)
        source = file_name
        if self.__CSL is None:
            import ctypes
            csl = ctypes.windll.kernel32.CreateSymbolicLinkW
            csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
            csl.restype = ctypes.c_ubyte
            self.__CSL = csl
        flags = 0
        if source is not None and os.path.isdir(source):
            flags = 1
        if self.__CSL(target, source, flags) == 0:
            raise ctypes.WinError()
    """
    def symlink(self, link, target, hardlink=False):
        import subprocess
        command = "cmd /c mklink "
        if hardlink:
            command = command + "/h "
        command = command + link + " " + target
        subprocess.call(command, shell=False)
    def SvcDoRun(self):
        """
        import servicemanager

        f = open('test2.dat', 'w+')

        f.write('TEST DATA\n')
        f.write('TEST DATA\n')
        f.write('TEST DATA\n')
        f.write('TEST DATA\n')
        f.write('TEST DATA\n')
        f.flush()

        f.write('SHUTTING DOWN\n')
        f.write('PS: CLEMENS IST EIN NOOB :)))) \n')
        f.close()
        """
        self.symlink("E:\\SymlinkTests\\typo3HARTERLINKUS", "E:\\typo3_src-7.4.0\\ChangeLog")

        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('start')
            self.start()
            self.log('wait')
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            self.log('done')
        except Exception, x:
            self.log('Exception : %s' % x)
            self.SvcStop()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.log('stopping')
        self.stop()
        self.log('stopped')
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def start(self):
        self.runflag=True
        while self.runflag:
            self.sleep(10)
            self.log("I'm alive ...")

    def stop(self):
         self.runflag=False
         self.log("I'm done")

if __name__ == '__main__':
     win32serviceutil.HandleCommandLine(Service)