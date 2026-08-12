nextflow.enable.dsl = 2

params.outdir = null

process SMOKE_HAP {
    container 'wave.seqera.io/wt/6a51dfcd00c7/wave/build:f8430331c4739c51'
    cpus 1
    memory '1 GB'
    publishDir params.outdir, mode: 'copy'

    output:
    path 'hap-version.txt'
    path 'hap-germline-help.txt'
    path 'hap-somatic-help.txt'

    script:
    """
    hap --version > hap-version.txt
    hap germline --help > hap-germline-help.txt
    hap somatic --help > hap-somatic-help.txt
    """

    stub:
    """
    touch hap-version.txt hap-germline-help.txt hap-somatic-help.txt
    """
}

workflow {
    if (!params.outdir) {
        error 'The --outdir parameter is required.'
    }
    SMOKE_HAP()
}
