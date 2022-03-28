
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from lib.tools import check_file
from lib.linux_cmd import cmd_run
from lib.config import TestConfig
con=TestConfig()
ref=con.get_ref("gtx_index")
known_Mills=con.get_knownsites_vcf("known_Mills")
known_1000G=con.get_knownsites_vcf("known_1000G")
known_dbsnp=con.get_knownsites_vcf("known_dbsnp")

def modulerun(checkfile_list, output_file, cmd, logf):
    check_output = [check_file(f) for f in checkfile_list]
    if all(check_output):
        if check_file(output_file):
            return True
        else:
            with open(os.path.join(os.path.dirname(logf), 'gtx_run.sh'), 'a') as fp:
                fp.writelines(cmd + '\n\n')
            return cmd_run(cmd, logf)
    else:
        print('please check the input file')



class GtxStep():
    def __init__(self,sample,output_path,gtx,CPU=72):
        self.CPU=CPU
        self.output_path=output_path
        self.sample=sample
        self.gtx=gtx



    def Align(self,r1,r2):
        output_file=f'{self.output_path}/{self.sample}.bam'
        check_list=[r1,r2]
        cmd = f'''{self.gtx} align -R '@RG\\tID:{self.sample}\\tSM:{self.sample}\\tPL:ILLUMINA' {ref} {r1} {r2} -M -Y -o {self.output_path}/{self.sample}.bam'''
        logf=f'{self.output_path}/{self.sample}.align.log'
        return modulerun(check_list, output_file, cmd, logf)

    def Bqsr(self):
        output= f'{self.output_path}/{self.sample}.sort.dup.bqsr'
        check_list = [f'{self.output_path}/{self.sample}.bam']
        cmd = f'''{self.gtx} bqsr -r {ref} -i {self.output_path}/{self.sample}.bam --known-sites {known_Mills} --known-sites {known_1000G} --known-sites {known_dbsnp} \
              -o {output}.bam --bqsr {output}.recal.grp'''
        logf = f'{self.output_path}/{self.sample}.bqsr.log'
        output_file=f'{output}.bam'
        return modulerun(check_list, output_file, cmd, logf)

    def Wgs(self,r1,r2,bed='',is_keep_bam=False):
        output = f'{self.output_path}/{self.sample}'
        check_list = [r1, r2]
        cmd = f'''{self.gtx} wgs -R '@RG\\tID:{self.sample}\\tSM:{self.ample}\\tPL:ILLUMINA' {ref} {r1} {r2} -o {output}.vcf.gz \
            -M -Y --bqsr {output}.recal.grp --known-sites {known_Mills} --known-sites {known_1000G} --known-sites {known_dbsnp} '''
        if bed:
            cmd=cmd+f' -L {bed}'
        if is_keep_bam:
            cmd=cmd+f' -b {output}.sort.dup.bqsr.bam'
        logf = f'{self.output_path}/{self.sample}.align.log'
        output_file=f'{output}.vcf.gz'
        return modulerun(check_list, output_file, cmd, logf)




if __name__ == '__main__':
    pass
