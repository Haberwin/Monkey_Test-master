# -*-coding:utf-8 -*-
import configparser
import os
import platform
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from time import sleep
import traceback


def clear_log(start_time, log_path):
    logFileList = []
    exceptionFileList = []
    for _ in log_path.iterdir():
        if _.is_dir() and datetime.strptime(_.name, "%Y%m%d_%H%M%S") >= start_time:
            # print(_)
            for logFile in _.glob(r'**/*.zip'):
                # print(logFile.name)
                if "_net.zip" in logFile.name or "_exception.zip" in logFile.name:
                    exceptionFileList.append(logFile)
                    if len(logFileList) > 0:
                        logFileList.pop()
                else:
                    logFileList.append(logFile)

    print(logFileList)
    for f in logFileList:
        print(f'Delete file {f.name}')
        f.unlink()
    print(exceptionFileList)
