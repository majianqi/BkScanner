#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Bin.lib.portcrack.portcrackbase import PortCrackBase
from Plugins.iPluginBase import PluginBase
from common.threadpool import ThreadPool
from common.util import getCurTime
from config.db_settings import PORTCRACK_TABLE

__all__ = ['MssqlCrackPlugin']

class MssqlCrackPlugin(PluginBase):

    name = "MssqlCrackPlugin"
    version = '1.0'

    def __init__(self):
        PluginBase.__init__(self)

        self.user_dict = 'mssqluser.txt'
        self.pass_dict = 'password.txt'
        self.service   = 'mssql'
        self.threadpool = ThreadPool(num_of_threads= 5 , num_of_work= 10 , daemon = True)
        self.portlist = ['1433', '1434']

    def execute_run(self, ip, port, taskid):
        if str(port) in self.portlist:
            mssqlcrack = PortCrackBase(self.user_dict, self.pass_dict)
            self.threadpool.add_job(mssqlcrack.crack, ip = ip, port = port, service = self.service)
            self.async_deal_into_db(taskid)

    def async_deal_into_db(self, taskid):
        '''
        异步入库
        :return:
        '''
        while not self.threadpool.resultQueue.empty():
            try:
                result_dit = self.threadpool.resultQueue.get_nowait()
                portcrack_dic = {}
                portcrack_dic['sid'] = taskid
                portcrack_dic['host'] = result_dit['ip']
                portcrack_dic['port'] = result_dit['port']
                portcrack_dic['username'] = result_dit['username']
                portcrack_dic['password'] = result_dit['password']
                portcrack_dic['service'] = self.service
                portcrack_dic['first_time'] = getCurTime()
                self.plugin_db.insert_by_dict(PORTCRACK_TABLE, portcrack_dic)
            except:
                break


    def wait_for_complete(self):
        PluginBase.wait_for_complete(self)
        self.db_close()