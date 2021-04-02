# -*- coding:utf-8 -*-
import traceback
from smb.SMBConnection import SMBConnection


class SmbCommunicate(object):
    """
    smb连接客户端
    """
    user_name = ''
    pwd = ''
    ip = ''
    port = None
    status = False
    samba = None

    def __init__(self, user_name, pwd, ip, port=139):
        self.user_name = user_name
        self.pwd = pwd
        self.ip = ip
        self.port = port

    def connect(self):
        try:
            self.samba = SMBConnection(
                self.user_name, self.pwd, '', '', use_ntlm_v2=True)
            self.samba.connect(self.ip, self.port)
            self.status = self.samba.auth_result
            if self.status:
                print("Connect SMB server Success!")
            else:
                print("Connect SMB server Fail!")
        except Exception:
            traceback.print_exc()
            print("Connect SMB server Fail!")
            self.samba.close()

    def disconnect(self):
        if self.status:
            self.samba.close()

    def all_file_names_in_dir(self, service_name, dir_name):
        """
        列出文件夹内所有文件名
        :param service_name:
        :param dir_name:
        :return:
        """
        f_names = list()
        for e in self.samba.listPath(service_name, dir_name):
            if len(e.filename) > 3:
                f_names.append(e.filename)
        return f_names

    def download_file(self, file_path, upload_dir, upload_path):
        """
        下载文件
        :param upload_path:
        :param upload_dir:
        :param file_path: 保存到本地文件的路径
        :return:c
        """
        try:
            self.connect()
            with open(file_path, 'wb') as file_obj:
                self.samba.retrieveFile(upload_dir, upload_path, file_obj)
            print("Download Success!")
            return True
        except Exception:
            traceback.print_exc()
            print("Download Fail!")
            return False

    def upload_file(self, file_path, upload_dir, upload_path):
        """
        上传文件
        :param upload_dir:
        :param file_path:
        :param upload_path: 上传文件的路径
        :return:True or False
        """
        try:
            self.connect()
            with open(file_path, 'rb') as file_obj:
                print(
                    "Upload File from {0} to {1}/{2}".format(file_path, upload_dir, upload_path))
                self.samba.storeFile(upload_dir, upload_path, file_obj)

            print("Upload file success!")
            return True
        except Exception:
            traceback.print_exc()
            print("Upload file Fail!")
            return False

    def create_folder(self, service_dir, create_path):
        """
        添加文件夹
        :param service_dir : root dir
        :param create_path :target path
        """
        try:
            self.connect()
            self.samba.createDirectory(service_dir, create_path)
            print("Create folder Success!")
            return True
        except Exception:
            traceback.print_exc()
            print("Create folder Fail!")
            return False

    def list_path(self, service_name, path):
        try:
            self.connect()
            for file_name in self.samba.listSnapshots(service_name, path):
                print(file_name)
        except Exception:
            traceback.print_exc()
            print("Create Fail!")
            return False


if __name__ == "__main__":
    smb = SmbCommunicate('liuwenhua', '98502', '192.168.4.3', 139)
    smb.connect()
    # smb.uploadFile("MTBF-log.zip", "Temp", "/LWH/MTBF-log.zip")
    # smb.creat_floder("Temp", "/Test2/")
    # smb.list_path("Temp", "LWH")
    smb.disconnect()
