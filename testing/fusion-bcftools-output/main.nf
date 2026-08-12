nextflow.enable.dsl = 2

process BCFTOOLS_OUTPUT_AB {
    tag 'direct-vs-redirected'
    container 'community.wave.seqera.io/library/bcftools_htslib:0a3fa2654b52006f'

    output:
    path '*.vcf'

    script:
    """
    printf '##fileformat=VCFv4.2\n##contig=<ID=chr1,length=1000>\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE_A\nchr1\t10\t.\tA\tC\t50\tPASS\t.\tGT\t0/1\n' | bgzip -c > a.vcf.gz
    printf '##fileformat=VCFv4.2\n##contig=<ID=chr1,length=1000>\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE_B\nchr1\t20\t.\tG\tT\t60\tPASS\t.\tGT\t0/1\n' | bgzip -c > b.vcf.gz
    tabix -p vcf a.vcf.gz
    tabix -p vcf b.vcf.gz

    bcftools merge --output-type v --force-samples --output direct.vcf a.vcf.gz b.vcf.gz
    bcftools merge --output-type v --force-samples --output - a.vcf.gz b.vcf.gz > redirected.vcf
    """
}

workflow {
    BCFTOOLS_OUTPUT_AB()
}
