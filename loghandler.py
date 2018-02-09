# -*- coding: utf8 -*-
u'''
Created on 2016年9月12日 下午6:43:59

@author: shaofeng.yang
'''
from logging import FileHandler
from logging.handlers import TimedRotatingFileHandler
import time
import os

class SafeFileHandler(FileHandler):
     def __init__(self, filename, mode, encoding=None, delay=0):
         """
         Use the specified filename for streamed logging
         """
         # if codecs is None:
         #     encoding = None
         FileHandler.__init__(self, filename, mode, encoding, delay)
         self.mode = mode
         self.encoding = encoding
         self.suffix = "%Y-%m-%d"
         self.suffix_time = ""

     def emit(self, record):
         """
         Emit a record.

         Always check time
         """
         try:
             if self.check_baseFilename(record):
                 self.build_baseFilename()
             FileHandler.emit(self, record)
         except (KeyboardInterrupt, SystemExit):
             raise
         except:
             self.handleError(record)

     def check_baseFilename(self, record):
         """
         Determine if builder should occur.

         record is not used, as we are just comparing times,
         but it is needed so the method signatures are the same
         """
         timeTuple = time.localtime()

         if self.suffix_time != time.strftime(self.suffix, timeTuple) or not os.path.exists(self.baseFilename+'.'+self.suffix_time):
             return 1
         else:
             return 0
     def build_baseFilename(self):
         """
         do builder; in this case,
         old time stamp is removed from filename and
         a new time stamp is append to the filename
         """
         if self.stream:
             self.stream.close()
             self.stream = None

         # remove old suffix
         if self.suffix_time != "":
             index = self.baseFilename.find("."+self.suffix_time)
             if index == -1:
                 index = self.baseFilename.rfind(".")
             self.baseFilename = self.baseFilename[:index]

         # add new suffix
         currentTimeTuple = time.localtime()
         self.suffix_time = time.strftime(self.suffix, currentTimeTuple)
         self.baseFilename  = self.baseFilename + "." + self.suffix_time

         self.mode = 'a'
         if not self.delay:
             self.stream = self._open()

class SafeRotatingFileHandler(TimedRotatingFileHandler):
     def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
         TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, delay, utc)
     """
     Override doRollover
     lines commanded by "##" is changed by cc
     """
     def doRollover(self):
         """
         do a rollover; in this case, a date/time stamp is appended to the filename
         when the rollover happens.  However, you want the file to be named for the
         start of the interval, not the current time.  If there is a backup count,
         then we have to get a list of matching filenames, sort them and remove
         the one with the oldest suffix.

         Override,   1. if dfn not exist then do rename
                     2. _open with "a" model
         """
         if self.stream:
             self.stream.close()
             self.stream = None
         # get the time that this sequence started at and make it a TimeTuple
         currentTime = int(time.time())
         dstNow = time.localtime(currentTime)[-1]
         t = self.rolloverAt - self.interval
         if self.utc:
             timeTuple = time.gmtime(t)
         else:
             timeTuple = time.localtime(t)
             dstThen = timeTuple[-1]
             if dstNow != dstThen:
                 if dstNow:
                     addend = 3600
                 else:
                     addend = -3600
                 timeTuple = time.localtime(t + addend)
         dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
    ##        if os.path.exists(dfn):
    ##            os.remove(dfn)

         # Issue 18940: A file may not have been created if delay is True.
    ##        if os.path.exists(self.baseFilename):
         if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
             os.rename(self.baseFilename, dfn)
         if self.backupCount > 0:
             for s in self.getFilesToDelete():
                 os.remove(s)
         if not self.delay:
             self.mode = "a"
             self.stream = self._open()
         newRolloverAt = self.computeRollover(currentTime)
         while newRolloverAt <= currentTime:
             newRolloverAt = newRolloverAt + self.interval
         #If DST changes and midnight or weekly rollover, adjust for this.
         if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
             dstAtRollover = time.localtime(newRolloverAt)[-1]
             if dstNow != dstAtRollover:
                 if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                     addend = -3600
                 else:           # DST bows out before next rollover, so we need to add an hour
                     addend = 3600
                 newRolloverAt += addend
         self.rolloverAt = newRolloverAt