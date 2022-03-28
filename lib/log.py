#coding=utf-8
'''
1. 配置log输出格式 time - loglevel - file - func - line - msg
2. 支持输出到log文件及屏幕
3. 支持返回一个logger,让其他模块调用
'''
from common.config import TestConfig
import logging, logging.handlers, time, os,sys
from colorama import Fore,Style
import sys,os
# 相对导入包的问题
#取项目的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))#存放c.py所在的绝对路径
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)




class LogInfo(TestConfig):
    def __init__(self):
        c = TestConfig()
        self.level = c.get_log("log_level")
        self.logger = logging.getLogger()
        # 设置输出的等级
        LEVELS = {'NOSET': logging.NOTSET,
                  'DEBUG': logging.DEBUG,
                  'INFO': logging.INFO,
                  'WARNING': logging.WARNING,
                  'ERROR': logging.ERROR,
                  'CRITICAL': logging.CRITICAL}

        # log_path是存放日志的路径
        timestr = time.strftime('%Y_%m_%d', time.localtime(time.time()))
        lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs'))
        # 如果不存在这个logs文件夹，就自动创建一个
        if not os.path.exists(lib_path):
            os.mkdir(lib_path)
        # 日志文件的地址
        self.logname = lib_path + '/' + timestr + '.log'

        # 必须设置，这里如果不显示设置，默认过滤掉warning之前的所有级别的信息
        self.logger.setLevel(LEVELS[self.level])

        # 日志输出格式
        self.formatter = logging.Formatter(
            '[%(asctime)s]: %(message)s')  # [2019-05-15 14:48:52,947]  - ERROR: this is error
        #设置日志入文件
        self.file_handler = logging.FileHandler(self.logname)

        if not self.logger.handlers:
            ch = logging.StreamHandler(sys.stdout)
            # 设置handler的格式对象
            ch.setFormatter(self.formatter)
            # 将handler增加到logger中
            self.logger.addHandler(ch)
            # # 关闭打开的文件
            ch.close()


    def info(self, msg):
        self.logger.info(Fore.GREEN + "[INFO]: \n" + str(msg) + Style.RESET_ALL)

    def debug(self, msg):
        self.logger.debug(Fore.WHITE + "[DEBUG]: \n" + str(msg) + Style.RESET_ALL)

    def warning(self, msg):
        self.logger.warning("\033[38;5;214m" + "[WARNING]: \n" + str(msg) + "\033[m")

    def error(self, msg):
        self.logger.error(Fore.RED + "[ERROR]: \n" + str(msg) + Style.RESET_ALL)


    def critical(self, msg):
        self.logger.critical(Fore.RED + "[CRITICAL]: \n" + str(msg) + Style.RESET_ALL)


if __name__ == "__main__":
    logger = LogInfo()
    logger.info("this is info")
    logger.debug("this is debug")
    logger.error("this is error")
    logger.warning("this is warning")
    logger.critical("critical")
