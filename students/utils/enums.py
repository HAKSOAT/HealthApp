from enum import Enum


class BloodGroups(Enum):
    a_positive = 'A+'
    a_negative = 'A-'
    b_positive = "B+"
    b_negative = "B-"
    o_positive = "O+"
    o_negative = "O-"
    ab_positive = "AB+"
    ab_negative = "AB-"


class GenoTypes(Enum):
    AA = 'AA'
    AS = 'AS'
    AC = 'AC'
    SS = 'SS'
    SC = 'SC'
    CC = 'CC'


class StudentLevels(Enum):
    first_year = '100L'
    second_year = '200L'
    third_year = '300L'
    fourth_year = '400L'
    fifth_year = '500L'
    sixth_year = '600L'


class Departments(Enum):
    ele = 'ELE'
    mte = 'MTE'
    mce = 'MCE'
    abe = 'ABE'
    cve = 'CVE'
    bch = 'BCH'
    mcb = 'MCB'
    paz = 'PAZ'
    pab = 'PAB'



class Colleges(Enum):
    coleng = 'COLENG'
    colbios = 'COLBIOS'
    colphys = 'COLPHYS'
    colvet = 'COLVET'
    colfhec = 'COLFHEC'
    colmas = 'COLMAS'
    colerm = 'COLERM'
    colanim = 'COLANIM'
    colamrud = 'COLAMRUD'
    colplant = 'COLPLANT'

