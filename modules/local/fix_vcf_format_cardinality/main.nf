process FIX_VCF_FORMAT_CARDINALITY {
    tag "$meta.id"
    label 'process_low'

    container 'community.wave.seqera.io/library/bcftools_htslib:0a3fa2654b52006f'

    input:
    tuple val(meta), path(vcf)

    output:
    tuple val(meta), path('*.vcf.gz'), path('*.vcf.gz.tbi'), emit: vcf
    path 'fixed.header.vcf', emit: header
    tuple val("${task.process}"), val('bcftools'), eval("bcftools --version | sed '1!d; s/^.*bcftools //'"), topic: versions, emit: versions_bcftools

    script:
    def prefix = vcf.baseName - '.vcf'
    """
    bcftools view --header-only ${vcf} \
        | sed -E '/^##FORMAT=<ID=(BG_SB|SB),/ s/Number=R/Number=./' \
        > fixed.header.vcf
    bcftools reheader \
        --header fixed.header.vcf \
        ${vcf} \
        | bcftools view \
            --output-type z \
            --output ${prefix}.format-cardinality.vcf.gz
    bcftools index \
        --tbi \
        ${prefix}.format-cardinality.vcf.gz
    """

    stub:
    def prefix = vcf.baseName - '.vcf'
    """
    echo '' | gzip > ${prefix}.format-cardinality.vcf.gz
    touch ${prefix}.format-cardinality.vcf.gz.tbi
    """
}
