
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from lib.tools import check_file
from lib.linux_cmd import cmd_run
from lib.config import TestConfig
con=TestConfig()
bwa=con.get_soft("bwa")
ref=con.get_ref("bwa_index")
gatkFacade=con.get_soft("gatk_facade")
known_Mills=con.get_knownsites_vcf("known_Mills")
known_1000G=con.get_knownsites_vcf("known_1000G")
known_dbsnp=con.get_knownsites_vcf("known_dbsnp")

def modulerun(checkfile_list, output_file, cmd, logf):
    check_output = [check_file(f) for f in checkfile_list]
    if all(check_output):
        if check_file(output_file):
            return True
        else:
            with open(os.path.join(os.path.dirname(logf), 'bwa_gatk_run.sh'), 'a') as fp:
                fp.writelines(cmd + '\n\n')
            return cmd_run(cmd, logf)
    else:
        print('please check the input file')



class GatkStep():
    def __init__(self,sample,output_path,CPU=72):
        self.CPU=CPU
        self.output_path=output_path
        self.sample=sample

    def bam_index(self,bam):
        checkfile_list=[bam]
        output=f"{self.output_path}/{bam.strip().split('/')[-1]}"
        logf=f'{output}.index.log'
        output_file=f'{bam}.bai'
        cmd=f"samtools index {bam} -@ {str(self.CPU)}"
        return modulerun(checkfile_list,output_file,cmd,logf)

    def align_sort(self,r1,r2):
        output=f"{self.output_path}/{self.sample}.sort"
        checkfile_list=[r1,r2]
        output_file=f'{output}.bam'
        cmd=f'''{bwa} mem -t {str(self.CPU)} -M -Y -K 10000000 -R '@RG\\tID:{self.sample}\\tSM:{self.sample}\\tPL:ILLUMINA' \
             {ref} {r1} {r2} | samtools sort -o {output}.bam -@ {str(self.CPU)}'''
        logf=f'{output}.log'
        if modulerun(checkfile_list,output_file,cmd,logf):
            return GatkStep(self.sample,self.output_path).bam_index(f'{output}.bam')




    def Gatk_MarkDuplicates(self,gatk):
        checkfile_list=[f'{self.output_path}/{self.sample}.sort.bam']
        output=f'{self.output_path}/{self.sample}.sort.dup'
        output_file=f'{output}.bam'
        logf=f'{output}.log'
        cmd=f'''{gatk} MarkDuplicates -I {self.output_path}/{self.sample}.sort.bam \
                -O {output}.bam -M {output}.out'''
        if modulerun(checkfile_list,output_file,cmd,logf):
            return GatkStep(self.sample,self.output_path).bam_index(f'{output}.bam')


    def Gatk_bqsr(self,gatk):
        checkfile_list = [f'{self.output_path}/{self.sample}.sort.dup.bam']
        output = f'{self.output_path}/{self.sample}.sort.dup.bqsr'
        output_file1 = f'{output}.grp'
        output_file2 = f'{output}.bam'
        logf1 = f'{output}.BaseRecalibrator.log'
        logf2=f'{output}.ApplyBQSR.log'
        cmd1 = f'''{gatk} BaseRecalibrator -I {self.output_path}/{self.sample}.sort.dup.bam -R {ref} \
                 --known-sites {known_Mills} --known-sites {known_1000G} --known-sites {known_dbsnp} -O {output}.grp '''
        cmd2=f'''{gatk} ApplyBQSR -R {ref} -I {self.output_path}/{self.sample}.sort.dup.bam \
                  --bqsr-recal-file {output}.grp -O {output}.bam'''
        if modulerun(checkfile_list,output_file1,cmd1,logf1):
            if modulerun(checkfile_list,output_file2,cmd2,logf2):
                return True
            else:
                print('ApplyBQSR ERROR!!')
        else:
            print('BaseRecalibrator ERROR!!' )

    def Gatk_HaplotypeCaller(self,gatk,bed=''):
        checkfile_list = [f'{self.output_path}/{self.sample}.sort.dup.bqsr.bam']
        output = f'{self.output_path}/{self.sample}'
        output_file = f'{output}.vcf.gz'
        logf = f'{output}_HaplotypeCaller.log'
        cmd =f'''python3 {gatkFacade} HaplotypeCaller -R {ref} -I {self.output_path}/{self.sample}.sort.dup.bqsr.bam \
            -O {output}.vcf.gz'''
        if bed:
            cmd = f'{cmd} -L {bed}'
        os.environ['GATK_LOCAL_JAR']=f'{gatk.strip().split()[-1]}'
        print(os.environ['GATK_LOCAL_JAR'])
        return modulerun(checkfile_list,output_file,cmd,logf)


if __name__ == '__main__':
    gatk_run=GatkStep('HG001','./')
    gatk_run.Gatk_bqsr()
