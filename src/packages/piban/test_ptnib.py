# test_ptnib.py  (c)2021  Henrique Moreira

""" Testing ptnib.py
"""

import sys
from piban.ptnib import slimIBAN, verify_check_digit, valid_iban

# pylint: disable=invalid-name

UNICEF_IBAN = "PT50 0033 0000 5013 1901 2290 5"	# UNICEF IBAN in Portugal


def main():
    """ Main script """
    param = sys.argv[1:]
    code = test_pt_nib(param)
    if code:
        print()
        sys.stderr.write(f"Error-code: {code}\n")
    sys.exit(code)


def test_pt_nib(args):
    """ Just a test function!
    """
    code = 0
    if not args:
        ibanStr = UNICEF_IBAN
    else:
        ibanStr = ' '.join(args)
    if not ibanStr.strip():
        return 0
    si = slimIBAN(ibanStr)
    isUNICEF = si.nib == UNICEF_IBAN.replace(" ", "")[4:]
    print(
        "Entered IBAN: {}{}\n{}".
        format(
            ibanStr, " <<< Please donate to UNICEF!" if isUNICEF else "",
            "--" * 20,
            ),
    )
    if si.clutter:
        print("Clutter len#" + str(len(si.clutter)) + ":", si.clutter)
    print(
        "NIB:", si.nib,
        "Valid?", si.validNIB,
        "CRC_ok?", si.validCRC,
        "; All valid?", si.all_valid(),
    )
    print("s:\t{}".format(si.s))
    print("niban:\t{}".format(si.niban))
    rNIB = si.readable_nib()
    print(
        ("--" * 20) + "\n" + "Readable NIB:", rNIB if rNIB else "<error>",
        "\n" + ("--" * 20),
    )
    print()
    tup = verify_check_digit(si.niban)
    assert len(tup) == 3
    isOk = tup[0]
    isNIB = tup[1]
    digitsKK = tup[2]
    if digitsKK:
        digitsKK = f"'{digitsKK}'"
    else:
        digitsKK = "<empty KK>"
    print(
        "verify_check_digit():", isOk,
        "; isNIB:", isNIB, "; IBAN?", valid_iban(si.niban),
        "; check digits:", digitsKK,
    )
    print("NIBAN:", si.niban)
    code = 0 if si.all_valid() else 1
    if not isOk:
        return 2
    return code


if __name__ == "__main__":
    main()
