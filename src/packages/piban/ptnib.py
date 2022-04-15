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

MIN_NIB_LENGTH = 21


class slimIBAN():
    """ slimIBAN class
    """
    def __init__(self, data=""):
        self._clutter = ""
        self.cLetters = ""
        self.nib = ""
        self.validNIB = False
        self.niban = data
        self.validCRC = False
        self.s = None
        if isinstance(data, str):
            self.s = data
            self.niban = self.set_iban_or_nib(data)

    def all_valid(self):
        return self.validNIB and self.validCRC

    def calc_check_digit(self, nr19):
        """ Calculates check digits from 19-digit NIB """
        return IbanMethods().calc_check_digit(nr19)

    def min_nib_length(self) -> int:
        """ Returns the minimum NIB length;
		(not IBAN length; IBAN length is 25 in PT)
        """
        return MIN_NIB_LENGTH

    def __str__(self) -> str:
        """ Returns the country IBAN, in a readable way """
        astr = self.readable_nib()
        if not astr:
            return ""
        if len(self.nib) <= self.min_nib_length():
            prefix = IbanMethods.prefix_for()
            if prefix:
                prefix = f"{prefix} "
            astr = prefix + astr
        else:
            astr = self.niban[:4] + " " + astr
        return astr

    def __repr__(self) -> str:
        astr = self.__str__()
        return f"'{astr}'"

    def readable_nib(self):
        if not self.all_valid():
            return ""
        s = self.nib
        return s[:4] + " " + s[4:8] + " " + s[8:19] + " " + s[19:]

    def get_clutter(self) -> str:
        """ Returns clutter (if any), a string. Empty means ok! """
        return self._clutter

    def set_iban_or_nib(self, aStr):
        nStr = trim_number(aStr)
        cCode = ""
        dig = ""
        nibOk = False
        self.validNIB = False
        self.validCRC = False
        onlyDigitsNow = False
        self._clutter = ""
        for c in nStr:
            if c.isdigit():
                dig += c
                onlyDigitsNow = True
            elif 'A' <= c <= 'Z':
                if onlyDigitsNow:
                    self._clutter += c
                else:
                    cCode += c
        fullStr = cCode + dig
        isOk = len(fullStr) >= 21 and not self._clutter
        if not isOk:
            return ""
        if cCode == IbanMethods().country_abbrev:
            nibOk = True
            self.nib = fullStr[4:]
        if not nibOk:
            if len(fullStr) >= self.min_nib_length():
                self.nib = fullStr[len(cCode):]
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
    def prefix_for(country:str="") -> str:
        assert isinstance(country, str)
        if not country:
            country = IbanMethods.country_abbrev
        candidates = []
        for key in sorted(VALID_IBAN_PREFIXES):
            item = VALID_IBAN_PREFIXES[key]
            if country == item:
                return key
            abbrev = f''.join(filter(str.isalpha, key))
            if not abbrev:
                continue
            if country == abbrev:
                candidates.append(key)
        if len(candidates) > 1 or not candidates:
            return ""
        return candidates[0]

    @staticmethod
    def calc_check_digit_pt(nr19):
        weight = [73, 17, 89, 38, 62, 45, 53, 15, 50, 5, 49, 34, 81, 76, 27, 90, 9, 30, 3]
        assert isinstance(nr19, str)
        aNum = nr19
        aLen = len(aNum)
        if aLen == 19:
            rememberAB = aNum
        elif aLen == 21:
            rememberAB = aNum[0:19]
        else:
            #print(f"calc_check_digit() failed (len#={len(nr19)}): '{nr19}'")
            return [False, -1, "", ""]
        if all_digits(aNum[0:19]):
            aSum = 0
            for idx in range(19):
                aSum += (weight[idx] * (ord(aNum[idx]) - ord('0')))
            c_dig = 98 - (aSum % 97)
            if c_dig < 10:
                cdStr = "0" + str(c_dig)
            else:
                cdStr = str(c_dig)
            return (True, cdStr, c_dig, (rememberAB + cdStr))
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
