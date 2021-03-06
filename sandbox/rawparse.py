#! /usr/bin/python3


#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
#                              HEAD                                     #
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
import os
import time
import subprocess
from subprocess import PIPE, STDOUT
import shlex
from time import sleep
import RPi.GPIO as GPIO
from random import *
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import re
import config as cfg

#-------------------------------#
#         GET CGM DATA          #
#*******************************#
def queryCgmData():

  #cast date and correct for timezone bug
  rawImport  =  subprocess.check_output(["wget","-q","-O","-",
    "https://glucalarm.herokuapp.com/api/v1/entries/current/?token=raspi-97846cb04ad59b51"])
  castTab    = re.compile("[^\t]+")
  rawParts   = castTab.findall(rawImport)

  #TODO -- if cant parse, access tthen no data
  
  #take timestamp
  #currently heroky reports only in 'z' or UTC time
  timeStr    = rawParts[0][1:20]
  tmpTime    = datetime.strptime(timeStr, '%Y-%m-%dT%H:%M:%S')
  tmpTime    = tmpTime.replace(tzinfo = timezone('UTC'))
  cfg.bsTime = tmpTime.astimezone(timezone('US/Eastern'))

  # if data is older than X min, no data
  if datetime.now()-timedelta(minutes=cfg.noDataTh) > cfg.bsTime:
    cfg.bsData = False
  else:
    cfg.bsData = True

  #cast bs
  tval        = rawParts[2]
  cfg.bsValue = int(tval,base = 10)

  #cast trend and drop
  cfg.bsTrend = rawParts[3][1:-1]

  if cfg.bsTrend == "DoubleUp":
    cfg.bsDirec = 1
    cfg.bsDrop  = 2
  elif cfg.bsTrend == "SingleUp":
    cfg.bsDirec = 1
    cfg.bsDrop  = 1
  elif cfg.bsTrend == "FortyFiveUp":
    cfg.bsDirec = 2
    cfg.bsDrop  = 0
  elif cfg.bsTrend == "Flat":
    cfg.bsDirec = 3
    cfg.bsDrop  = 0
  elif cfg.bsTrend == "FortyFiveDown":
    cfg.bsDirec = 4
    cfg.bsDrop  = 0
  elif cfg.bsTrend == "SingleDown":
    cfg.bsDirec = 5
    cfg.bsDrop  = 1
  elif cfg.bsTrend == "DoubleDown":
    cfg.bsDirec = 5
    cfg.bsDrop  = 2
#-----------------------------------------------#

#-------------------------------#
#          PRINT DATA           #
#*******************************#
def printCgmData():
  while True:
    queryCgmData()
    print('time {}'.format(cfg.bsTime))
    print('data {}'.format(cfg.bsData))
    print('value {}'.format(cfg.bsValue))
    print('trendT {}'.format(cfg.bsTrend))
    print('trend {}'.format(cfg.bsDirec))
    print('drop {}'.format(cfg.bsDrop))
    #print('pwrBt press dur {:8.2f}'.format(td), flush=True)
    time.sleep(5)    
#-----------------------------------------------#

#-------------------------------#
#          INIT FUNC            #
#*******************************#
#if excecuted as script
if __name__=='__main__':
  printCgmData()
#-----------------------------------------------#

#EOF#
