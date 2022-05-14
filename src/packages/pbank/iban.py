# iban.py  (c)2022  Henrique Moreira

""" IBAN class(es)
See also: https://www.iban.com/iban-checker
"""

# pylint: disable=missing-function-docstring


class IBAN():
    """ IBAN european numerical accounts
    - International Bank Account Number
    Reference: ISO 13616:1997
    """
    def __init__(self, iban_str=None):
        astr = iban_str.replace(" ", "") if iban_str else ""
        self._iban = astr
        self._bstr = ""
        if iban_str:
            trip = IbanCalcMethod().ban_mod97(astr)
            _, self._value, self._bstr = trip
        else:
            self._value = -1
        #print("bstr is:", self._bstr)

    def get(self) -> str:
        return self._iban

    def bban(self) -> str:
        """ Returns the BBAN: Basic Bank Account Number """
        bstr = self._bstr
        if not bstr:
            return ""
        res = bstr[-4:]
        if not res[0].isalpha():
            return ""
        assert res.isupper(), bstr
        return res

    def value(self) -> int:
        return self._value

    def check_digit_ok(self):
        return self.bban() and self._value % 97 == 1

    def check_digits(self):
        bstr = self._bstr
        assert bstr
        # position 3 and 4 of the bstr
        return bstr[2:4]

    def modulus(self):
        val, _, _ = IbanCalcMethod().ban_mod97(self._iban)
        return val

class IbanCalcMethod():
    """ CRC method (basic 97 modulus!)
    """
    _shortest_iban_length = 15	# see https://www.iban.com/structure (Norway)

    @staticmethod
    def ban_mod97(iban) -> tuple:
        """ Return a triple:
		IBAN modulus
		the numerical value
		bstr (4 iban chars at the right side)
        """
        assert isinstance(iban, str)
        assert len(iban) > 4, f"IBAN too short: {iban}"
        bstr = iban[4:] + iban[:4]
        transtr = IbanCalcMethod().ban_translate(bstr)
        anum = int(transtr)
        val = anum % 97
        return val, anum, bstr

    @staticmethod
    def ban_translate(astr) -> str:
        """ IBAN translate function
        """
        res = ""
        for uchr in astr:
            if uchr.isdigit():
                val = ord(uchr) - ord('0')
            else:
                # there are 26 letters; letter 'A' is string '10'
                val = ord(uchr) - ord('A') + 10
                assert 10 <= val <= 35, "Invalid IBAN:" + astr
            res += str(val)
        return res

    @staticmethod
    def calculate_check_digits(iban:str) -> str:
        """ Calculate check digits, from yet incomplete IBAN
        """
        bstr = iban[4:] + iban[:4]
        new = IbanCalcMethod().calculate_cdigits(bstr)
        return new[-4:] + new[:-4]

    @staticmethod
    def calculate_cdigits(bstr) -> str:
        """ Calculate check digits, from yet incomplete bstr
        Example: 5121080012451261DE00
        IBAN is: DE75512108001245126199
        """
        if len(bstr) < IbanCalcMethod()._shortest_iban_length:
            return ""  # error!
        new = bstr[:-2] + "00"
        trans = IbanCalcMethod().ban_translate(new)
        amod = int(trans) % 97
        check_digit_value = 98 - amod
        res = "{}{:02}".format(
            bstr[:-2],
            check_digit_value,
        )
        # Returns the complete bstr with check digits
        return res

    @staticmethod
    def bstr_to_iban(bstr) -> str:
        if len(bstr) < IbanCalcMethod()._shortest_iban_length:
            return ""  # error!
        return bstr[-4:] +  bstr[:-4]

def calc_check_digits(iban:str) -> str:
    return IbanCalcMethod().calculate_check_digits(iban)
