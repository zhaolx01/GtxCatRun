
import subprocess,os,sys



def check_file(file):
    #print(file,'!!!!!!!!!!!')
    if os.path.exists(file):
        return True
    else:
        print(f'{file} no exist!')


def IsNum(str):
    s=str.split('.')
    if len(s)>2:
        return False
    else:
        for si in s:
            if not si.isdigit():
                return False
        return True

def check_file_consistency(f1,f2):
    #将文件中的有#的行和空行删除
    if check_file(f1) and check_file(f2):

        cmd1=f'''grep -v "#" {f1} |grep -v "^$" >/tmp/tmp1_{os.path.basename(f1)}'''
        cmd2 = f'''grep -v "#" {f2} |grep -v "^$" >/tmp/tmp2_{os.path.basename(f2)}'''
        os.system(cmd1)
        os.system(cmd2)
        with open(f'/tmp/tmp1_{os.path.basename(f1)}',"r") as fp1:
            with open(f'/tmp/tmp2_{os.path.basename(f2)}',"r") as fp2:
                data1=fp1.readlines()
                data2=fp2.readlines()
                res=[]
                if len(data1)==len(data2):
                    for line in range(len(data1)):
                        l1=data1[line].strip().split()
                        l2=data2[line].strip().split()
                        l1=[float(i) if IsNum(i) else i for i in l1]
                        l2 =[float(j) if IsNum(j) else j for j in l2]
                        if l1==l2:
                            res.append(True)
                        else:
                            res.append(False)
                            print('the different rows:',line)
                            print(l1)
                            print(l2)
                            for item in range(len(l1)):
                                if l1[item]!=l2[item]:
                                    print('the column:',item)
                                    print(l1[item],l2[item])
                    if all(res):
                        return True
                    else:
                        return False

                else:
                    print('The file length is inconsistent ！！')
    else:
        print('file no exist:',f1,f2)




if __name__=="__main__":
    f1=sys.argv[1]
    f2=sys.argv[2]
    print(check_file_consistency(f1, f2))
