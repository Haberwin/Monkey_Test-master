# -*-coding:utf-8 -*-
import configparser
import os
import platform
import subprocess
import urllib
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path
from time import sleep
import traceback
from pandas import DataFrame

import pandas as pd
import zipfile

pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', 200)
pd.set_option('display.width', 300)


class ParseLog(object):
    Exception_list = []  # 存储dbg文件列表
    Frame = DataFrame(
        columns=['type', 'source', 'package', 'info', 'time', 'file_path'])
    Issue_Subject = ""
    Issue_Description = ""
    Dbg_File_List = []  # 存储Dbg文件
    ParseDir_List = []  # 存储已经解析过的文件夹
    zip_folder = []  # 存储已经压缩过的文件夹

    def __init__(self, aee_path, log_path):

        self.log_path = log_path
        self.aee_path = aee_path

    def check_log(self, start_time):
        for _ in self.log_path.iterdir():
            if _.is_dir() and datetime.strptime(_.name, "%Y%m%d_%H%M%S") >= datetime.strptime(start_time, "%Y%m%d_%H%M%S"):
                self.ParseDir_List.append(_)
                for zip_file in _.glob(r'**/*_exception.zip*'):
                    print(f"Extract zip file: {zip_file}")
                    with zipfile.ZipFile(zip_file, 'r') as z:
                        z.extractall(zip_file.with_name(
                            zip_file.name.replace(".zip", "")))
                    for dbg_file in _.glob(r'**/*.dbg'):
                        self.Exception_list.append(dbg_file)
                        # self.parse_log(dbg_file)
                        self.Dbg_File_List.append(dbg_file.absolute())
                        print("Find dbg file:\n{}".format(dbg_file))
                        for zz_internal in dbg_file.parent.glob(r'ZZ_INTERNAL*'):
                            with zz_internal.open(mode='r') as f:
                                result = f.read()
                                # print(result)
                                tmp_list = result.split(',')
                                try:
                                    self.Frame = self.Frame.append(
                                        {'file_path': dbg_file.relative_to(self.log_path), 'type': tmp_list[0],
                                         'source': tmp_list[4], 'package': tmp_list[6],
                                         'info': tmp_list[7], 'time': tmp_list[8]}, ignore_index=True)
                                except IndexError:
                                    print(f"Abnormal file:{zz_internal}")
                    self.Issue_Subject = '[bug](monkey test)Total Error:{};'.format(
                        self.Frame['type'].value_counts()).replace('Name: type, dtype: int64', '')
                    self.Issue_Description = "Summary:\n{}".format(self.Frame)
            print(self.Issue_Description)
            with open("Report.txt", "w") as report:
                report.write(self.Issue_Description)
                report.flush()

    def create_issue(self, redmine_url, project_issue, assigned_to):
        """
        创建bug
        参数 redmine_url:redmine服务器地址
        参数 project_issue:目标项目下的一个issue号
        参数 assigned_to:指派人的账号
        """
        if check_url(redmine_url) and not self.Frame.empty:
            from Modules.CreateRedmine import CreateRedmine

            monkey_bug = CreateRedmine(redmine_url=redmine_url)
            monkey_bug.set_project_id(project_issue)
            monkey_bug.set_parameter(subject=self.Issue_Subject, description=self.Issue_Description,
                                     assigned=assigned_to)
            monkey_bug.creat_isses()
            print("Create issue success.")

    def parse_log(self):
        if not self.Dbg_File_List:
            print("No .dbg file found!")
            return
        for dbg_file in self.Dbg_File_List:
            subprocess.Popen('{exec_aee} {arg}'.format(
                exec_aee=self.aee_path, arg=dbg_file), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def zip_and_upload(self, smb, root_path, shard, folder, list_dbg=None):
        """
        压缩并上传log
        :param smb: smb服务器地址
        :param root_path:放置压缩文件的根目录
        :param shard:SMB服务器的Shard目录，如Temp
        :param folder:SMB Shard目录下防止zip文件的路径，如 log/monkey-log
        :param list_dbg:存放dbg文件的列表
        """

        print("start zip")
        if not list_dbg:
            print("No dbg file found!")
            return
        main_root = os.getcwd()
        os.chdir(str(root_path))
        print(os.getcwd())
        zip_name = str(root_path) + '.zip'
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
            print("list")
            print(list_dbg)
            for dgb_file in list_dbg:
                # if root_path not in dgb_file.parents:
                #     continue
                for exp_folder in dgb_file.parents:
                    if str(exp_folder).endswith("exception") and exp_folder not in self.zip_folder:
                        for f in exp_folder.rglob('*'):
                            z.write(str(f.relative_to(root_path)))
                            print('zip file:{}'.format(f))
                        self.zip_folder.append(exp_folder)
        smb.upload_file(
            zip_name, shard, "{0}/{1}.zip".format(folder, root_path.name))
        print("remove file:{}".format(zip_name))
        os.remove(zip_name)
        os.chdir(main_root)


def check_url(test_url):
    opener = urllib.request.build_opener()
    opener.add_handler = []
    # test_url = 'http://192.168.3.75:8006/redmine'
    try:
        opener.open(test_url, timeout=3)
        print('Network connection available:{}'.format(test_url))
        return True
    except urllib.error.HTTPError:
        print('无法访问{}'.format(test_url))
        return False
    except urllib.error.URLError:
        print('无法访问{}'.format(test_url))
        return False
    except Exception as err:
        print(err)
        return False


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('setting.ini', encoding='utf-8-sig')
    # print(config.sections)
    project_issue = config.get('Redmine', 'project issue')
    create_bug = config.get('Redmine', 'create bug')
    start_time = config.get('monkey', 'start time')
    assigned_to = config.get('Redmine', 'assigned to id')
    redmine_url = config.get('Redmine', 'url')
    upload_log = config.get('SMBServer', 'uploadlog')
    smb_url = config.get('SMBServer', 'url')
    smb_port = int(config.get('SMBServer', 'port'))
    smb_user = config.get('SMBServer', 'name')
    smb_psw = config.get('SMBServer', 'password')
    smb_shard = config.get('SMBServer', 'shard')
    upload_path = config.get('SMBServer', 'logpath')
    log_path = Path.cwd() / 'log' / 'MTBF-log'
    aee_program = 'aee_parse_linux' if platform.system().__eq__(
        'Linux') else 'aee_parse_win.exe'
    aee_path = Path.cwd().parent / 'aeeParse' / aee_program

    parse = ParseLog(aee_path, log_path)
    try:
        print(start_time)
        # ":\\\\{url}\{shard}{dir}\\".format(url=smb_url, shard=smb_shard, dir=upload_path))
        parse.check_log(start_time)
        is_parse_log = input(
            "Do you want to parse .dbg files now?(Input Y/N ,Default N)")
        if is_parse_log.upper() == "Y":
            parse.parse_log()
        print('Parse log succeed!')
        if len(parse.Exception_list) > 0:
            if create_bug == 'true':
                parse.create_issue(redmine_url, project_issue, assigned_to)
            if upload_log == 'true':
                from Modules.SmbCommunicate import SmbCommunicate

                smb = SmbCommunicate(smb_user, smb_psw, smb_url, smb_port)
                try:
                    for log_dir in parse.ParseDir_List:
                        parse.zip_and_upload(
                            smb, log_dir, smb_shard, upload_path, parse.Exception_list)
                finally:
                    smb.disconnect()
    except Exception:
        traceback.print_exc()
        print("Parse Fail!")

    for _ in range(10):
        print('Process will exit after {} second!'.format(10 - _))
        sleep(1)
