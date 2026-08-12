process HAPPY_SOMPY {
    tag "$meta.id"
    label 'process_medium'

    container 'wave.seqera.io/wt/07b660e5a317/wave/build:158cf20a25a302b3'

    input:
    tuple val(meta), path(query_vcf), path(truth_vcf), path(regions_bed), path(targets_bed)
    tuple val(meta2), path(fasta)
    tuple val(meta3), path(fasta_fai)
    tuple val(meta4), path(false_positives_bed)
    tuple val(meta5), path(ambiguous_beds)
    tuple val(meta6), path(bams)

    output:
    tuple val(meta), path('*.features.csv')           , emit: features, optional: true
    tuple val(meta), path('*.metrics.json')           , emit: metrics
    tuple val(meta), path('*.stats.csv')              , emit: stats
    tuple val("${task.process}"), val('hap-rs'), val('0.1.0'), topic: versions, emit: versions_happy

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    def regions = regions_bed ? "-R ${regions_bed}" : ""
    def targets = targets_bed ? "-T ${targets_bed}" : ""
    def false_positives = false_positives_bed ? "--false-positives ${false_positives_bed}" : ""
    def ambiguous = ambiguous_beds ? "--ambiguous ${ambiguous_beds}" : ""
    def bams_opt = bams ? "--bam ${bams}" : ""
    """
    export HAP_RS_PROFILE=1
    hap somatic \\
        ${truth_vcf} \\
        ${query_vcf} \\
        ${args} \\
        --reference ${fasta} \\
        ${regions} \\
        ${targets} \\
        ${false_positives} \\
        ${ambiguous} \\
        ${bams_opt} \\
        -o ${prefix}

    """

    stub:
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    touch ${prefix}.features.csv
    touch ${prefix}.metrics.json
    touch ${prefix}.stats.csv

    """
}
