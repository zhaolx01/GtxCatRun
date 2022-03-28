#coding=utf-8
'''
1. 从配置文件中获取各个段信息
2. 返回一个项目的绝对路径
'''
from configparser import ConfigParser
import sys,os
# 相对导入包的问题
#所有路径转为绝对路径
#取项目的绝对路径
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))#存放c.py所在的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


# pro_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
filename="default.conf"


class TestConfig(ConfigParser):

    def __init__(self):
        self.cf = ConfigParser()
        self.cf.read(os.path.join(BASE_DIR, "conf", filename))


    def get_items(self,item):
        return self.cf.items(item)

    def get_project_info(self,option):
        return self.cf.get("PROJECT_INFO", option)

    def get_analysis(self, option):
        return os.path.join(BASE_DIR,self.cf.get("ANALYSIS", option))

    def get_data(self, option):
        return os.path.join(BASE_DIR,self.cf.get("DATA", option))

    def get_soft(self,option):
        return os.path.join(BASE_DIR,self.cf.get("SOFT", option))

    def get_ref(self,option):
        return os.path.join(BASE_DIR,self.cf.get("REF", option))

    def get_knownsites_vcf(self,option):
        return os.path.join(BASE_DIR,self.cf.get("knownsites_vcf", option))

    def get_docker(self,option):
        return self.cf.get("docker_lib", option)



if __name__ == "__main__":
    c = TestConfig()
    print(BASE_DIR)
    print(c.get_soft("gtx_verison_path"))
