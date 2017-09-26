#!/usr/bin/pyton3.5
"""Module designed to handle the copy of the files"""
from pathlib import Path
from shutil import copy2
from ftputil import FTPHost
from modules.DbHandler.DbHandler import DbHandler

class FilesCopier(object):
    """Files Copier Class"""

    def __init__(self):
        self.database = DbHandler()
        self.target = None
        self.source = None

    def start(self, target, source):
        """Main method of copy class.
            This method check the type of connection with the target and handle it accordly"""
        self.target = target
        self.source = source
        if not target.get('type'):
            print("Type of copy is not defined in the config target section. Please fix this problem and try again")
            exit(0)
        elif target.get('type') == 'local':
            if self.copy_local_files():
                self.database.clear()
                print("File transfer completed successfully")
            else:
                print("Some files could not be copied. Please try again later")
        elif target.get('type') == 'ftp':
            if self.copy_remote_files():
                self.database.clear()
                print("File transfer completed successfully")
            else:
                print("Some files could not be copied. Please try again later")

    def copy_local_files(self):
        """Process the copy where the target is the localhost"""
        if not self.target.get("path"):
            self.print_path_not_found_error()
        else:
            src_path = self.source.get('path')
            tgt_path = self.target.get('path')
            dirs = self.database.getPendingDirs()
            try:
                for directory in dirs:
                    new_dir = directory['path'].replace(src_path, tgt_path)
                    Path(new_dir).mkdir(parents=True, exist_ok=True)
                    if Path(new_dir).exists():
                        files = self.database.getPendingFiles(directory.doc_id)
                        for file in files:
                            new_file = file['path'].replace(src_path, tgt_path)
                            if self.source.get('type') == 'local':
                                copy2(file['path'], new_file)
                            else:
                                self.download_file(file['path'], new_file)
                            if Path(new_file).exists():
                                self.database.markAsCreated('files', file['path'])
                            else:
                                print("The file %s could not be copied. Aborting"%file['path'])
                                exit(0)
                        self.database.markAsCreated('dirs', directory['path'])
                    else:
                        print("The dir %s could not be created. Aborting"%new_dir)
                        exit(0)
                return True
            except PermissionError:
                self.print_permission_denied_error()

    def copy_remote_files(self):
        """Process the copy of the files where the target is a remote server"""
        if not self.target.get("path"):
            self.print_path_not_found_error()
        else:
            src_path = self.source.get('path')
            tgt_path = self.target.get('path')
            dirs = self.database.getPendingDirs()
            for directory in dirs:
                new_dir = directory['path'].replace(src_path, tgt_path)
                with FTPHost(self.target.get('address'), self.target.get('user'), self.target.get('password')) as client:
                    client.makedirs(new_dir)
                    if client.path.isdir(new_dir):
                        files = self.database.getPendingFiles(directory.doc_id)
                        for file in files:
                            new_file = file['path'].replace(src_path, tgt_path)
                            if self.source.get('type') == 'ftp':
                                tmp_file = "/tmp/%s" % file['path'].split('/')[-1]
                                self.download_file(file['path'], tmp_file)
                                if Path(tmp_file).exists():
                                    client.upload(tmp_file, new_file)
                                    Path(tmp_file).unlink()
                            else:
                                client.upload(file['path'], new_file)
                            if client.path.isfile(new_file):
                                self.database.markAsCreated('files', file['path'])
                            else:
                                print("The file %s could not be copied. Aborting"%file['path'])
                                exit(0)
                        self.database.markAsCreated('dirs', directory['path'])
                    else:
                        print("The dir %s could not be created. Aborting"%new_dir)
                        exit(0)
            return True

    def download_file(self, src, tgt):
        """Do the file download from a remote server"""
        with FTPHost(self.source.get('address'), self.source.get('user'), self.source.get('password')) as client:
            client.download(src, tgt)

    def print_path_not_found_error(self):
        """Print the path not found error and stops the program execution"""
        print("The target path is not a valid path")
        exit(0)

    def print_permission_denied_error(self):
        """Print the permission denied error and stops the program execution"""
        print("I can't access some of directory that you specified. Please execute-me with another user")
        exit(0)
