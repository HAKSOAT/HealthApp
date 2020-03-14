from enum import Enum


class Departments(Enum):
    # COLENG
    ele = 'ELE'
    mte = 'MTE'
    mce = 'MCE'
    abe = 'ABE'
    cve = 'CVE'
    # COLBIOS
    bch = 'BCH'
    mcb = 'MCB'
    paz = 'PAZ'
    pab = 'PAB'
    # COLERM
    emt = 'EMT'
    wma = 'WMA'
    aqfm = 'AQFM'
    fwm = 'FWM'
    # COLAMRUD
    agad = 'AGAD'
    aefm = 'AEFM'
    aerd = 'AERD'
    # COLMAS
    eco = 'ECO'
    ets = 'ETS'
    acc = 'ACC'
    bfn = 'BFN'
    bam = 'BAM'
    # COLPHYS
    chm = 'CHM'
    csc = 'CSC'
    mts = 'MTS'
    phs = 'PHS'
    sts = 'STS'
    # COLANIM
    abg = 'ABG'
    ann = 'ANN'
    anp = 'ANP'
    aph = 'APH'
    prm = 'PRM'
    # COLPLANT
    sslm = 'SSLM'
    ppcp = 'PPCP'
    pbst = 'PBST'
    hrt = 'HRT'
    cpt = 'CPT'
    # COLFHEC
    fst = 'FST'
    hsm = 'HSM'
    ntd = 'NTD'
    htm = 'HTM'
    # COLVET
    vet = 'VET'


class UserTypes(Enum):
    student = 'Student'
    worker = 'Worker'
