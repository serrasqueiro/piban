# ptnib.py  (c)2022  Henrique Moreira


""" ptnib module for portuguese NIB

  Simplified from niban.py and formerly part of 'paccount'

  Note:
     IBAN is a standard, ISO 13616
"""

# pylint: disable=missing-function-docstring, invalid-name


VALID_IBAN_PREFIXES = {
    "PT50": "Portugal",
}


class slimIBAN():
    """ slimIBAN class
    """
    def __init__(self, data=""):
        self.clutter = ""
        self.cLetters = ""
        self.nib = ""
        self.validNIB = False
        self.minNIB_length = 21
        self.niban = data
        self.validCRC = False
        self.s = None
        if isinstance(data, str):
            self.s = data
            self.niban = self.set_iban_or_nib(data)

    def all_valid(self):
        return self.validNIB and self.validCRC

    def calc_check_digit(self, nr19):
        return IbanMethods().calc_check_digit(nr19)

    def readable_nib(self):
        if not self.all_valid():
            return ""
        s = self.nib
        return s[:4] + " " + s[4:8] + " " + s[8:19] + " " + s[19:]

    def set_iban_or_nib(self, aStr):
        nStr = trim_number(aStr)
        cCode = ""
        dig = ""
        nibOk = False
        self.validNIB = False
        self.validCRC = False
        onlyDigitsNow = False
        self.clutter = ""
        for c in nStr:
            if c.isdigit():
                dig += c
                onlyDigitsNow = True
            elif 'A' <= c <= 'Z':
                if onlyDigitsNow:
                    self.clutter += c
                else:
                    cCode += c
        fullStr = cCode + dig
        isOk = len(fullStr) >= 21 and not self.clutter
        if not isOk:
            return ""
        if cCode == IbanMethods().country_abbrev:
            nibOk = True
            self.nib = fullStr[4:]
        if not nibOk:
            if len(fullStr) >= self.minNIB_length:
                self.nib = fullStr[len( cCode ):]
                nibOk = cCode == ""
        if self.nib:
            nr19 = self.nib[:-2]
            tup = self.calc_check_digit(nr19)
            self.validCRC = tup[3] == self.nib
            self.validNIB = nibOk
        return fullStr


class IbanMethods():
    """ IBAN methods class """
    country_abbrev = "PT"

    def calc_check_digit(self, nr19):
        """ calc. check digit from 19 digit number ('NIBwoD')
		- Portugal, see https://www.bportugal.pt/page/iban
        """
        if IbanMethods.country_abbrev == "PT":
            return IbanMethods.calc_check_digit_pt(nr19)
        return (False, "", -1, "", -1)

    @staticmethod
    def calc_check_digit_pt(nr19):
        weight = [73, 17, 89, 38, 62, 45, 53, 15, 50, 5, 49, 34, 81, 76, 27, 90, 9, 30, 3]
        if isinstance(nr19, str):
            triple = [False, nr19, 0]
        else:
            triple = nr19
        assert len(triple) == 3
        aNum = triple[1]
        aLen = len(aNum)
        if aLen == 19:
            rememberAB = aNum
        else:
            if aLen == 21:
                rememberAB = aNum[0:19]
            else:
                return [False, -1, "", ""]
        if all_digits(aNum[0:19]):
            aSum = 0
            i = 0
            while i < 19:
                aSum += (weight[i] * (ord(aNum[i])-ord('0')))
                i += 1
            cd = 98 - (aSum % 97)
            if cd < 10:
                cdStr = "0" + str(cd)
            else:
                cdStr = str(cd)
            return (True, cdStr, cd, (rememberAB + cdStr))
        return (False, "", -1, "?", aNum)

    @staticmethod
    def ban_bcmod97(iban) -> int:
        """ Banco de Portugal NIB calculation
        """
        assert isinstance(iban, str)
        assert len(iban) > 4, f"IBAN too short: {iban}"
        bstr = iban[4:] + iban[:4]
        transtr = IbanMethods().ban_translate(bstr)
        anum = int(transtr)
        val = anum % 97
        print("anum:", anum, "; val:", val, "; bstr:", bstr)
        return val

    @staticmethod
    def ban_translate(b) -> str:
        """ BAN translate function
        """
        res = ""
        for u in b:
            if u.isdigit():
                v = ord(u) - ord('0')
            else:
                # there are 26 letters; letter 'A' is string '10'
                v = ord(u) - ord('A') + 10
                if v < 10 or v >= 36:
                    return "0"
            res += str(v)
        return res


def verify_check_digit(nibStr):
    """ Verifies check digit from NIB:
    returns tuple (True|False, isNIB, checkDigit)
    """
    if not isinstance(nibStr, str):
        return (False, False, "")
    si = slimIBAN()
    nStr = nibStr.strip()
    aLen = len( nStr )
    isNIB = aLen==21
    isIBAN = aLen==25 and valid_iban_prefix(nStr[0:4])
    nib = ""
    if isIBAN:
        nib = nStr[4:]
    if isNIB:
        nib = nStr
    if nib == "":
        return (False, False, "")
    dgt = si.calc_check_digit(nib[0:19])
    dgtKK = dgt[1]
    isOk = dgtKK==nib[19:]
    return (isOk, isNIB, dgtKK)


def valid_iban(iban) -> int:
    """ Returns 1 if IBAN is valid
    """
    assert isinstance(iban, str)
    if len(iban) < 15:
        return -1  # Too short!
    ccOk = valid_iban_prefix(iban[:4])
    if ccOk:
        ccKK = IbanMethods().ban_bcmod97(iban)
        return ccKK
    return -1

def valid_iban_prefix(nStr) -> bool:
    """ Returns True if prefix of IBAN 'nStr' is valid.
    """
    assert isinstance(nStr, str)
    try:
        isOk = nStr in VALID_IBAN_PREFIXES
    except NameError:
        isOk = nStr == "PT50"
    return isOk


def trim_number(aNum) -> str:
    """ Ignore blanks and dots, returns the trimmed string.
    """
    if not isinstance(aNum, str):
        return str(aNum)
    iStr = aNum
    aStr = ""
    for aChr in iStr:
        if aChr in (' ', '.'):
            continue
        aStr += aChr
    return aStr


def all_digits(aStr):
    return aStr.isdigit()


if __name__ == "__main__":
    print("Import me!")
