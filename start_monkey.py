# -*-coding:utf-8
import subprocess
import os
import sys
import re
import configparser
from datetime import datetime
from pathlib import Path
import threading
import platform
from time import sleep
import traceback
import logging
from Modules import ClearLog


#os.chdir(os.path.dirname(sys.argv[0]))

config = configparser.ConfigParser()
config.read('setting.ini', encoding='utf-8-sig')
log_path = Path.cwd()/ 'log'
run_path = Path.cwd()
start_time = datetime.now()


# print(config.sections())
test_time = re.findall(r'\d+', config.get('monkey', 'test time'))


def start_monkey():
    """ Start Monkey"""
    devices = get_devices()
    if not devices:
        log.logger.info('No devices found. Exit')
        return
    else:
        with open('setting.ini', 'w') as f:
            config.set('monkey', 'start time',
                       value=start_time.strftime("%Y%m%d_%H%M%S"))
            config.write(f)
        log.logger.info("Find devices:\n{}".format(devices))
        assert_monkey_ps(True)
        thread_pull = threading.Thread(target=pull_mtklog)
        thread_pull.setDaemon(True)
        thread_pull.start()
        os.chdir(str(run_path))
        pull_times=0
        try:
            while True:
                pull_times+=1
                sys.stdout.flush()
                run_time = datetime.now() - start_time
                log.logger.info('Running time: {}s'.format(
                    run_time))
                if int(test_time[0]) * 3600 <= int(run_time.seconds):
                    log.logger.info("Test Timeout!")
                    break
                if not thread_pull.is_alive():
                    thread_pull = threading.Thread(target=pull_mtklog)
                    thread_pull.setDaemon(True)
                    thread_pull.start()
                assert_monkey_ps(True)
                sleep(300)
                if pull_times%24==0:
                    ClearLog.clear_log(start_time,log_path)
        except KeyboardInterrupt:
            log.logger.info('Monkey Interrupt because key Abort')
        except Exception:
            traceback.print_exc()
        finally:
            stop_pull()
            assert_monkey_ps(False)
            thread_pull.join()
            log.logger.info('Monkey test finished!')
            for _ in range(10):
                log.logger.info('Process will exit after {} seconds!'.format(10 - _))
                # log.logger.info(thread_pull.is_alive()) 
                sleep(1)
            log.logger.info('Exit!')


def get_devices():
    pipe = subprocess.Popen(
        'adb devices', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if not pipe.stderr:
        log.logger.info('No adb found,please install adb! Abort test')
        return False
    devices = re.findall(r'\s(\S+)\tdevice',
                         pipe.stdout.read().decode('utf-8'))
    return devices


def run_monkey(serial_no):
    log.logger.info("Push blacklist...")
    subprocess.Popen(f'adb -s {serial_no} push blacklist.txt /sdcard/', shell=True)
    monkey_command = config.get('monkey', 'command')
    # log.logger.info('adb -s {0} shell {1} '.format(serial_no, monkey_command))
    start_time_str=start_time.strftime("%Y%m%d%H%M%S")
    run_cmd = f'start /b adb -s {serial_no} shell "{monkey_command}>> {log_path}/Monkey-log/monkey-{serial_no}-{start_time_str}.txt'
    if platform.system().__eq__('Linux'):
        run_cmd = f'adb -s {serial_no} shell "{monkey_command}>> {log_path}/Monkey-log/monkey-{serial_no}-{start_time_str}.txt &'
    log.logger.info(run_cmd)
    subprocess.Popen(run_cmd,shell=True)


def assert_monkey_ps(is_continue=True):
    devices = get_devices()
    if not devices:
        log.logger.info('No devices found!')
        return
    assert_cmd = "adb -s {0} shell ps | findstr monkey"
    if platform.system().__eq__('Linux'):
        assert_cmd = 'adb -s {0} shell ps | grep monkey'
    for serial_no in devices:
        monkey_ps = subprocess.Popen(assert_cmd.format(serial_no), shell=True,
                                     stdout=subprocess.PIPE)
        is_monkey_run = False
        while True:
            ps_id = monkey_ps.stdout.readline()
            if ps_id:
                is_monkey_run = True
                if is_continue:
                    log.logger.info('Monkey still running in the devices {}'.format(serial_no))
                else:

                    pid = re.findall(
                        r'\d+', re.findall(r'shell\s+\d+', ps_id.decode('utf-8'))[0])[0]
                    subprocess.Popen('adb -s {0} shell kill {1}'.format(serial_no, pid), shell=True,
                                     stdout=subprocess.PIPE)
            else:
                if is_continue and not is_monkey_run:
                    log.logger.info('Restart monkey  in the devices {}'.format(serial_no))
                    run_monkey(serial_no)
                break

def pull_mtklog():
    try:
        log_exe = 'LoNg.jar'
        thread_pull_log = subprocess.Popen("java -jar {}".format(
            log_exe), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(log_path))

        while thread_pull_log.poll() is None:
            # log.logger.info("end")
            # log.logger.info(thread_pull_log.stderr.readline().decode('utf-8', 'ignore'))
            stderr = thread_pull_log.stderr.readline().decode('utf-8', 'ignore')
            print(stderr)
            log.logger.info(stderr)
    except Exception:
        thread_pull_log.terminate()
        log.logger.error("Thread pull log Abort")
        traceback.print_exc()
def stop_pull():
    stop_exe="CloseLoNg.jar"
    subprocess.run(f"java -jar {stop_exe}",shell=True, cwd=str(log_path))


import logging
from logging import handlers

class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,filename,level='info',when='D',backCount=3,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里


if __name__ == '__main__':
    log = Logger('test.log',level='debug')
    if not test_time:
        log.logger.info("Set running time {} Fail".format(test_time))
    else:
        log.logger.info("Set running time {}".format(test_time))
    # start_monkey()
    ClearLog.chear_log(start_time,log_path/'MTBF-log')
