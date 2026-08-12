nextflow.enable.dsl = 2

params.outdir = null
params.grch38_no_alt = 'https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/references/GRCh38/GCA_000001405.15_GRCh38_no_alt_analysis_set.fasta.gz'
params.grch37_hs37d5 = 'https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/references/GRCh37/hs37d5.fa.gz'
params.grch38_giabv3 = 'https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/references/GRCh38/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta.gz'

process STAGE_REFERENCE {
    tag "$name"
    container 'quay.io/biocontainers/samtools:1.22--h96c455f_0'
    cpus 1
    memory '4 GB'
    publishDir params.outdir, mode: 'copy'

    input:
    tuple val(name), path(source)

    output:
    tuple val(name), path("${name}.fasta"), path("${name}.fasta.fai"), path("${name}.sha256")

    script:
    """
    bgzip -cd ${source} > ${name}.fasta
    samtools faidx ${name}.fasta
    sha256sum ${name}.fasta ${name}.fasta.fai > ${name}.sha256
    """
}

workflow {
    if (!params.outdir) {
        error 'The --outdir parameter is required.'
    }
    references = Channel.of(
        tuple('grch38-noalt', file(params.grch38_no_alt, checkIfExists: true)),
        tuple('grch37-hs37d5', file(params.grch37_hs37d5, checkIfExists: true)),
        tuple('grch38-giabv3', file(params.grch38_giabv3, checkIfExists: true))
    )
    STAGE_REFERENCE(references)
}
