
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from lib.tools import check_file
from lib.linux_cmd import cmd_run
from lib.config import TestConfig


con=TestConfig()
GATK_all_path=con.get_soft("gatk_verison_path")
gatkFacade=con.get_soft("gatk_facade")
ref=con.get_ref("bwa_index")
germline_resource=con.get_knownsites_vcf("germline_resource")
ref_interval_list=con.get_knownsites_vcf("ref_interval_list")

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

class GatkMutect2():
    def __init__(self,output_path,normal_sample,tumor_sample,normal_bam,tumor_bam,gatk,bed='',is_clear=True,CPU=72):
        # os.environ['GATK_LOCAL_JAR'] = f'{gatk.strip().split()[-1]}'
        # print(os.environ['GATK_LOCAL_JAR'])
        self.CPU=CPU
        self.output_path=output_path
        self.is_clear=is_clear
        self.normal_sample=normal_sample
        self.tumor_sample=tumor_sample
        self.normal_bam=normal_bam
        self.tumor_bam=tumor_bam
        self.bed=bed
        self.gatk=gatk


    def Mutect2(self):
        output=f'''{self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2'''
        check_list=[self.normal_bam,self.tumor_bam]
        cmd=f'{self.gatk} Mutect2 -R {ref} --germline-resource {germline_resource} --normal-sample {self.normal_sample} --f1r2-tar-gz {output}.tar.gz --max-reads-per-alignment-start 0\
            -O {output}.vcf.gz -I {check_list[0]} -I {check_list[1]}'
        logf=f'{output}.log'
        output_file=f'{output}.vcf.gz'

        return modulerun(check_list,output_file, cmd, logf)

    def GetPileupSummaries_tumor(self):
        output = f'''{self.output_path}/{self.tumor_sample}_tumor.GetPileupSummaries'''
        check_list = [self.tumor_bam,ref_interval_list]
        if self.bed:
            cmd = f'{self.gatk} GetPileupSummaries -R {ref} -L {os.path.join(con.get_data("wes_mutect2_data"),self.bed)} -I {self.tumor_bam} -V {germline_resource} -O {output}.tsv'
        else:
            cmd = f'{self.gatk} GetPileupSummaries -R {ref} -L {ref_interval_list} -I {self.tumor_bam} -V {germline_resource} -O {output}.tsv'
        logf = f'{output}.log'
        output_file = f'{output}.tsv'
        return modulerun(check_list, output_file, cmd, logf)

    def GetPileupSummaries_normal(self):

        output = f'''{self.output_path}/{self.normal_sample}_normal.GetPileupSummaries'''
        check_list = [self.normal_bam, ref_interval_list]
        if self.bed:
            cmd = f'{self.gatk} GetPileupSummaries -R {ref} -L {os.path.join(con.get_data("wes_mutect2_data"),self.bed)} -I {self.normal_bam} -V {germline_resource} -O {output}.tsv'
        else:
            cmd = f'{self.gatk} GetPileupSummaries -R {ref} -L {ref_interval_list} -I {self.normal_bam} -V {germline_resource} -O {output}.tsv'
        logf = f'{output}.log'
        output_file = f'{output}.tsv'
        return modulerun(check_list, output_file, cmd, logf)

    def CalculateContamination(self):
        #CalculateContamination -I HCC1187BL_HCC1187C.tumor_pileups.tsv --matched-normal HCC1187BL_HCC1187C.normal_pileups.tsv
        # -O HCC1187BL_HCC1187C.contamination.table --tumor-segmentation HCC1187BL_HCC1187C.segments.table)
        output = f'''{self.output_path}/{self.normal_sample}_{self.tumor_sample}.CalculateContamination'''
        check_list = [f'{self.output_path}/{self.tumor_sample}_tumor.GetPileupSummaries.tsv',f'{self.output_path}/{self.normal_sample}_normal.GetPileupSummaries.tsv']
        cmd = f'{self.gatk} CalculateContamination -I {self.output_path}/{self.tumor_sample}_tumor.GetPileupSummaries.tsv --matched-normal {self.output_path}/{self.normal_sample}_normal.GetPileupSummaries.tsv \
             -O {output}.table --tumor-segmentation {output}.segments.table'
        logf = f'{output}.log'
        output_file = f'{output}.table'
        return modulerun(check_list, output_file, cmd, logf)

    def LearnReadOrientationModel(self):
        # LearnReadOrientationModel -I HCC1187BL_HCC1187C.f1r2.tar.gz -O HCC1187BL_HCC1187C.artifact-priors.tar.gz)
        output = f'''{self.output_path}/{self.normal_sample}_{self.tumor_sample}.LearnReadOrientationModel'''
        check_list = [f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.tar.gz']
        cmd = f'{self.gatk} LearnReadOrientationModel -I {self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.tar.gz -O {output}.tar.gz'
        logf = f'{output}.log'
        output_file = f'{output}.tar.gz'
        return modulerun(check_list, output_file, cmd, logf)


    def FilterMutectCalls(self):
        # f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.vcf.gz.stats'
        output = f'''{self.output_path}/{self.normal_sample}_{self.tumor_sample}.FilterMutectCalls'''
        check_list = [f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.vcf.gz',
                      f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.CalculateContamination.table',
                      f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.LearnReadOrientationModel.tar.gz',
                      f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.CalculateContamination.segments.table']
        cmd = f'{self.gatk} FilterMutectCalls -R {ref} -V {self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.vcf.gz \
               --contamination-table {self.output_path}/{self.normal_sample}_{self.tumor_sample}.CalculateContamination.table \
               --orientation-bias-artifact-priors {self.output_path}/{self.normal_sample}_{self.tumor_sample}.LearnReadOrientationModel.tar.gz \
               --stats {self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.vcf.gz.stats \
               --tumor-segmentation {self.output_path}/{self.normal_sample}_{self.tumor_sample}.CalculateContamination.segments.table \
               -O {output}.tar.gz \
               --filtering-stats {output}.tsv'
        logf = f'{output}.log'
        output_file = f'{output}.tar.gz'
        return modulerun(check_list, output_file, cmd, logf)











if __name__ == '__main__':
    pass
