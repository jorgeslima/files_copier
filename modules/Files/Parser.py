#!/usr/bin/pyton3.5
"""Handles the parse of the files. Scans a dir and generate the database of files to be copied"""

import time
from pathlib import Path
from ftputil import FTPHost
from paramiko import Transport,SFTPClient
from stat import S_ISDIR
from modules.DbHandler.DbHandler import DbHandler

class FilesParser(object):
    """Files parser class definition"""
    def __init__(self, source):
        self.database = DbHandler()
        self.dir_id = None
        self.source = source
        self.sftp = None
        self.transport = None
        source_type = source.get('type')
        if not source_type:
            print("Type of copy is not defined in the config source section. Please fix this problem and try again")
            exit(0)

    def parse_files(self):
        """Main class method"""
        source = self.source
        if source.get('type') == 'local':
            self.parse_local_host_files(source.get('path'))
            return True
        elif source.get('type') == 'ftp':
            self.parse_remote_ftp_files()
            return True
        elif source.get('type') == 'sftp':
            self.init_sftp_connection()
            self.parse_remote_sftp_files()
            self.close_sftp_connection()
            return True


    def parse_local_host_files(self, path):
        """Handle the scan of localhost files"""
        if not path:
            self.print_path_not_found_error()
        else:
            main_path = Path(path)
            if main_path.is_dir():
                if self.dir_id is None:
                    self.dir_id = self.database.insert('dirs', {'path':str(path), 'status':False})
                try:
                    for i in main_path.iterdir():
                        if i.is_dir():
                            self.dir_id = self.database.insert('dirs', {'path':str(i), 'status':False})
                            self.parse_local_host_files(i)
                        else:
                            self.database.insert('files', {'dir_id':self.dir_id, 'path':str(i), 'status':False})
                except PermissionError:
                    self.print_permission_denied_error()
            else:
                self.print_path_not_found_error()

    def parse_remote_ftp_files(self, root=None):
        """Handle the scan of remote files"""
        self.validate_remote_config()
        if not root:
            root = self.source.get('path')
        with FTPHost(self.source.get('address'), self.source.get('user'), self.source.get('password')) as client:
                for root_dir,dirs,files in client.walk(root):
                    self.dir_id = self.database.insert('dirs', {'path':root_dir, 'status':False})
                    for f in files:
                        nfile = "%s/%s" % (root_dir, f)
                        self.database.insert('files', {'dir_id':self.dir_id, 'path':nfile, 'status':False})

    def parse_remote_sftp_files(self,rpath=None):
        if not rpath:
            rpath = self.source.get('path')
        if self.dir_id is None:
            self.dir_id = self.database.insert('dirs', {'path':str(rpath), 'status':False})
        for f in self.sftp.listdir(rpath):
            try:
                rf = rpath+'/'+f
                if S_ISDIR(self.sftp.stat(rf).st_mode):
                    self.dir_id = self.database.insert('dirs', {'path':str(rf), 'status':False})
                    self.parse_remote_sftp_files(rf)
                else:
                    self.database.insert('files', {'dir_id':self.dir_id, 'path':str(rf), 'status':False})
            except IOError:
                pass

    def print_path_not_found_error(self):
        """Print the path not found error and stops the program execution"""
        print("The source path is not a valid path")
        exit(0)

    def print_permission_denied_error(self):
        """Print the permission denied error and stops the program execution"""
        print("I can't access some of directory that you specified. Please execute-me with another user")
        exit(0)

    def validate_remote_config(self):
        """Read and check if all the remote settings of the configuration are valid before use i"""
        has_error = True
        if not self.source.get('address'):
            print("Please inform the remote address of the server")
        elif not self.source.get('path'):
            print("The source path is not a valid path")
        elif not self.source.get('user'):
            print("Inform a valid user")
        elif not self.source.get('password'):
            print("Inform a valid password")
        else:
            has_error = False

        if has_error:
            exit(0)
        else:
            return True

    def init_sftp_connection(self):
        self.transport = Transport((self.source.get('address'),22))
        self.transport.connect(username=self.source.get('user'),password=self.source.get('password'))
        self.sftp = SFTPClient.from_transport(self.transport)

    def close_sftp_connection(self):
        self.sftp.close()
        self.transport.close()