#coding=utf-8
import subprocess,os,time,sys
# 相对导入包的问题
#取项目的绝对路径
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))#存放c.py所在的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)




def cmd_run(cmd,logf=''):
    print(cmd,'\n')
    cmd = f'''/usr/bin/time -v {cmd}'''
    a, b = subprocess.getstatusoutput(cmd)

    if logf:
        with open(f'{logf}','w+') as fg:
            fg.writelines(b+'\n\n\n')
    if a == 0:
        return True
    else:
        print(b, '\n\n\n')
        return False

def runCmd(cmd):
    try:
        a,stu=subprocess.getstatusoutput(cmd)
        if a==0:
            return True,stu
        else:
            return False,stu
    except Exception as e:
        print(e)



def runCmdInTime(cmd,t):
    '''

    :param cmd:
    :param t: timeout
    :param file_log: log file
    :return:
    '''
    file_log='/tmp/runCmdInTime.log'
    if os.path.exists(file_log):
        os.system(f'rm {file_log}')

    try:
        print(cmd)
        with open(file_log, 'w') as f:
            p = subprocess.Popen(cmd, shell=True, stdout=f, stderr=f)
            p.wait(timeout=t)
        with open(file_log,"r") as fp:
            return fp.read()

    except:
        with open(file_log,"r") as fp:
            return 'time out\n'+fp.read()



def runCmdToTimeInfo(cmd):
    t0 = time.time()
    stu=runCmd(cmd)
    if stu:
        dt = time.time() - t0
        return dt,stu





if __name__ == '__main__':
    print(BASE_DIR)
    cmd='ping 10.0.05.s'
    stu=runCmd(cmd)

