from __future__ import print_function
import os
import json
import shutil
import logging
import warnings
import subprocess
import datetime
import numpy as np

class bnBackupModule(object):

    def __init__(self, json_file, backup_path):
        logging.info('## Welcome to the Backup System Management ##')
        self.host_list = []
        self.json_file = json_file
        self.backup_path = backup_path 
        logging.info('## The backup directory is %s', self.backup_path)
        self.logs_path = os.path.join( self.backup_path, 'logs')
        if (not os.path.isdir(self.logs_path)):
            os.makedirs(self.logs_path)
        self.load_info()

    def rsync_conf(self):
        for computer in self.host_list:
            host = computer[0]
            home = "home" if computer[1]=="linux" else "Users"
            user = computer[2]
            logging.info('## Backup of the configuration of %s', host)
            path_to_host =  os.path.join(self.backup_path, '%s-%s'%(host, user))
            if (not os.path.isdir(path_to_host)):
                os.makedirs(path_to_host)
            cmd ='rsync --archive --verbose --human-readable --itemize-changes --progress \
            --delete %s@%s:/etc/hosts  %s/hosts 2>&1 > %s/rsync-output-conf-hosts-%s.txt '%(user, host, path_to_host, self.logs_path, user)
            subprocess.run(cmd, shell=True, universal_newlines=True, check=True)
            cmd ='rsync --archive --verbose --human-readable --itemize-changes --progress \
            --delete %s@%s:/etc/motd  %s/motd 2>&1 > %s/rsync-output-conf-motd-%s.txt'%(user, host, path_to_host, self.logs_path, user)
            subprocess.run(cmd, shell=True, universal_newlines=True, check=True)
            path_to_home_conf =  os.path.join(path_to_host, user)
            if (not os.path.isdir(path_to_home_conf)):
                os.makedirs(path_to_home_conf)
            cmd ='rsync --archive --verbose --exclude ".Trash" --exclude ".cache" --human-readable --itemize-changes --progress \
            --delete %s@%s:/%s/%s/.[^.]*  %s 2>&1 > %s/rsync-output-conf-%s.txt'%(user, host, home, user, path_to_home_conf, self.logs_path, user)
            subprocess.run(cmd, shell=True, universal_newlines=True, check=True)

        
    def rsync_modules(self, bkp_conf = True):      
        for (k, v) in self.json_info.items():
            logging.info('## I am starting backup of %s', k)
            user = v['user']
            host = v['host']
            host_os = v['os']
            self.host_list.append([host, host_os, user])
            src_path = v['src_path']
            logging.info('Backup for the user:host:  %s:%s ', user, host)
            logging.info('In the following source path %s', src_path)
            cmd = 'rsync --archive --verbose --human-readable --itemize-changes --progress \
            --delete %s@%s:%s %s/%s 2>&1 > %s/rsync-output-%s.txt'% (user, host, src_path, self.backup_path, k, self.logs_path, k)
            subprocess.run(cmd, shell=True, universal_newlines=True, check=True)
            logging.info("## The backup of %s is done!", k)
        if (bkp_conf):
            self.host_list = np.unique( self.host_list, axis = 0 )
            self.rsync_conf()   

    def load_info(self):
        with open(self.json_file) as f:
            self.json_info = json.load(f) 