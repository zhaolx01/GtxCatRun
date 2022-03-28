
import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from lib.tools import check_file
from lib.linux_cmd import cmd_run
from lib.config import TestConfig



con=TestConfig()
GATK_all_path=con.get_soft("gtx_version_path")
ref=con.get_ref("gtx_index")
germline_resource=con.get_knownsites_vcf("germline_resource")
ref_interval_list=con.get_knownsites_vcf("ref_interval_list")

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

class GtxMutect2():
    def __init__(self,output_path,normal_sample,tumor_sample,normal_bam,tumor_bam,gtx,bed='',is_clear=True,CPU=72):
        self.CPU=CPU
        self.output_path=output_path
        self.is_clear=is_clear
        self.normal_sample=normal_sample
        self.tumor_sample=tumor_sample
        self.normal_bam=normal_bam
        self.tumor_bam=tumor_bam
        self.bed=bed
        self.gtx=gtx


    def Mutect2(self):
        output=f'''{self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2'''
        check_list=[self.normal_bam,self.tumor_bam]
        cmd=f'{self.gtx} mutect2 -r {ref} -i {check_list[0]} -i {check_list[1]} --germline-resource {germline_resource} --normal-sample {self.normal_sample} \
             --f1r2-tar-gz {output}.tar.gz -o {output}.vcf.gz '
        logf=f'{output}.log'
        output_file=f'{output}.vcf.gz'
        return modulerun(check_list,output_file, cmd, logf)


    def Gps_tumor(self):
        #输出要以后缀table结尾
        output = f'''{self.output_path}/{self.tumor_sample}_tumor.GetPileupSummaries'''
        check_list = [self.tumor_bam,ref_interval_list]
        if self.bed:
            cmd = f'{self.gtx} gps -r {ref} -L {os.path.join(con.get_data("wes_mutect2_data"),self.bed)} -i {self.tumor_bam} -v {germline_resource} -o {output}.table'
        else:
            cmd = f'{self.gtx} gps -r {ref} -L {ref_interval_list} -i {self.tumor_bam} -v {germline_resource} -o {output}.table'
        logf = f'{output}.log'
        output_file = f'{output}.table'
        return modulerun(check_list, output_file, cmd, logf)

    def Gps_normal(self):

        output = f'''{self.output_path}/{self.normal_sample}_normal.GetPileupSummaries'''
        check_list = [self.normal_bam, ref_interval_list]
        if self.bed:
            cmd = f'{self.gtx} gps -r {ref} -L {os.path.join(con.get_data("wes_mutect2_data"),self.bed)} -i {self.normal_bam} -v {germline_resource} -o {output}.table'
        else:
            cmd = f'{self.gtx} gps -r {ref} -L {ref_interval_list} -i {self.normal_bam} -v {germline_resource} -o {output}.table'
        logf = f'{output}.log'
        output_file = f'{output}.table'
        return modulerun(check_list, output_file, cmd, logf)

    def Calc(self):

        output = f'''{self.output_path}/{self.normal_sample}_{self.tumor_sample}.CalculateContamination'''
        check_list = [f'{self.output_path}/{self.tumor_sample}_tumor.GetPileupSummaries.table',f'{self.output_path}/{self.normal_sample}_normal.GetPileupSummaries.table']
        cmd = f'{self.gtx} calc -i {self.output_path}/{self.tumor_sample}_tumor.GetPileupSummaries.table --matched-normal {self.output_path}/{self.normal_sample}_normal.GetPileupSummaries.table \
             -o {output}.table --tumor-segmentation {output}.segments.table'
        logf = f'{output}.log'
        output_file = f'{output}.table'
        return modulerun(check_list, output_file, cmd, logf)

    def Learn(self):
        output = f'''{self.output_path}/{self.normal_sample}_{self.tumor_sample}.LearnReadOrientationModel'''
        check_list = [f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.tar.gz']
        cmd = f'{self.gtx} learn -i {self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.tar.gz -o {output}.tar.gz'
        logf = f'{output}.log'
        output_file = f'{output}.tar.gz'
        return modulerun(check_list, output_file, cmd, logf)


    def Filter(self):
        output = f'''{self.output_path}/{self.normal_sample}_{self.tumor_sample}.FilterMutectCalls'''
        check_list = [f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.vcf.gz',
                      f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.CalculateContamination.table',
                      f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.LearnReadOrientationModel.tar.gz',
                      f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.vcf.gz.stats',
                      f'{self.output_path}/{self.normal_sample}_{self.tumor_sample}.CalculateContamination.segments.table']
        cmd = f'{self.gtx} filter -r {ref} -v {self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.vcf.gz \
               --contamination-table {self.output_path}/{self.normal_sample}_{self.tumor_sample}.CalculateContamination.table \
               --orientation-bias-artifact-priors {self.output_path}/{self.normal_sample}_{self.tumor_sample}.LearnReadOrientationModel.tar.gz \
               --stats {self.output_path}/{self.normal_sample}_{self.tumor_sample}.Mutect2.vcf.gz.stats \
               --tumor-segmentation {self.output_path}/{self.normal_sample}_{self.tumor_sample}.CalculateContamination.segments.table \
               -o {output}.vcf.gz \
               --filtering-stats {output}.filteringStats.tsv'
        logf = f'{output}.log'
        output_file = f'{output}.vcf.gz'
        return modulerun(check_list, output_file, cmd, logf)











if __name__ == '__main__':
    pass
