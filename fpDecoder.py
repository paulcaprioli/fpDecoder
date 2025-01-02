#!/usr/bin/env python3

#*******************************************************************************
# Copyright (C) 2020-2025 Paul Caprioli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#*******************************************************************************

import re, struct, sys

def FP64toQW(d):
    packed = struct.pack('>d', d)
    qw, = struct.unpack('>Q', packed)
    return qw

def QWtoFP64(qw):
    packed = struct.pack('>Q', qw)
    d, = struct.unpack('>d', packed)
    return d

def FP32toDW(f):
    packed = struct.pack('>f', f)
    dw, = struct.unpack('>I', packed)
    return dw

def DWtoFP32(dw):
    packed = struct.pack('>I', dw)
    f, = struct.unpack('>f', packed)
    return f

def FP16toW(e):
    packed = struct.pack('>e', e)
    w, = struct.unpack('>H', packed)
    return w

def WtoFP16(w):
    packed = struct.pack('>H', w)
    e, = struct.unpack('>e', packed)
    return e

def BF16toW(f):
    # User is expected to enter a value representable as a "brain float 16",
    # i.e. the lower 16 bits should be zero.  If not, do something reasonable.
    packed = struct.pack('>f', f)
    dw, = struct.unpack('>I', packed)  # Bits after converting to FP32
    w = dw >> 16
    if (dw & 0x7FFFFFFF) > 0x7F800000:  # NaN
        if (w & 0x7F) == 0:
            w |= (0x1 << 6)  # Set bit 6 to make the result NaN
    else:
        dw += 0x7FFF + (w & 0x1)  # RNE
        w = dw >> 16
    return w

def WtoBF16(w):
    dw = w << 16
    packed = struct.pack('>I', dw)
    f, = struct.unpack('>f', packed)
    return f

def BF8toB(e):
    # User is expected to enter a value representable as a "brain float 8",
    # i.e. the lower 8 bits should be zero.  If not, do something reasonable.
    packed = struct.pack('>e', e)
    w, = struct.unpack('>H', packed)  # Bits after converting to FP16
    b = w >> 8
    if (w & 0x7FFF) > 0x7C00:  # NaN
        if (b & 0x3) == 0:
            b |= (0x1 << 1)  # Set bit 1 to make the result NaN
    else:
        w += 0x7F + (b & 0x1)  # RNE
        b = w >> 8
    return b

def BtoBF8(b):
    w = b << 8
    packed = struct.pack('>H', w)
    e, = struct.unpack('>e', packed)
    return e

def decodeString(numberString, numberType):
    numberString = re.sub('_', '', numberString)
    if re.match("\s*epsilon", numberString, re.I):
        if numberType == "bf8":
            valueInt = 0x34
        if numberType == "bf16":
            valueInt = 0x3C00
        if numberType == "fp16":
            valueInt = 0x1400
        if numberType == "fp32":
            valueInt = 0x34000000
        if numberType == "fp64":
            valueInt = 0x3CB0000000000000
    elif '.' in numberString or 'n' in numberString or 'N' in numberString:
        try:
            if re.match("\s*[+-]*0x", numberString, re.I):
                inputValue = float.fromhex(numberString)
            else:
                inputValue = float(numberString)
        except:
            return (None, None)
        if numberType == "bf8":
            valueInt = BF8toB(inputValue)
        if numberType == "bf16":
            valueInt = BF16toW(inputValue)
        if numberType == "fp16":
            valueInt = FP16toW(inputValue)
        if numberType == "fp32":
            valueInt = FP32toDW(inputValue)
        if numberType == "fp64":
            valueInt = FP64toQW(inputValue)
    else:
        try:
            valueInt = int(numberString, 0)
        except:
            return (None, None)
    if numberType == "bf8":
        if valueInt < 0 or valueInt > 0xFF:
            return (None, None)
        return (valueInt, BtoBF8(valueInt))
    if numberType == "bf16":
        if valueInt < 0 or valueInt > 0xFFFF:
            return (None, None)
        return (valueInt, WtoBF16(valueInt))
    if numberType == "fp16":
        if valueInt < 0 or valueInt > 0xFFFF:
            return (None, None)
        return (valueInt, WtoFP16(valueInt))
    if numberType == "fp32":
        if valueInt < 0 or valueInt > 0xFFFFFFFF:
            return (None, None)
        return (valueInt, DWtoFP32(valueInt))
    if numberType == "fp64":
        if valueInt < 0 or valueInt > 0xFFFFFFFFFFFFFFFF:
            return (None, None)
        return (valueInt, QWtoFP64(valueInt))

def getHexValueString(valueFloat, numberType):
    if numberType == "bf8" or numberType == "bf16":
        return re.sub('00000000000p', 'p', valueFloat.hex())
    if numberType == "fp16":
        return re.sub('0000000000p', 'p', valueFloat.hex())
    if numberType == "fp32":
        return re.sub('0000000p', 'p', valueFloat.hex())
    return valueFloat.hex()

def printKey(prefix, numberType):
    spaces = re.sub('\S', ' ', prefix)
    if numberType == "bf8":
        print(prefix, "7 65432 10")
        print(spaces, "S -E5-- F2")
    if numberType == "fp16":
        print(prefix, "1       0")
        print(spaces, "5 43210 9876543210")
        print(spaces, "S -E5-- ---F10----")
    if numberType == "bf16":
        print(prefix, "1      0")
        print(spaces, "5 43210987 6543210")
        print(spaces, "S ---E8--- --F7---")
    if numberType == "fp32":
        print(prefix, "3  2          1         0")
        print(spaces, "1 09876543 21098765432109876543210")
        print(spaces, "S ---E8--- ----------F23----------")
    if numberType == "fp64":
        print(prefix, "6    5       ",
                      "  4         3         2         1         0")
        print(spaces, "3 21098765432",
                      "1098765432109876543210987654321098765432109876543210")
        print(spaces, "S ----E11----",
                      "------------------------F52-------------------------")

def crack(valInt, numberType):
    if numberType == "bf8":
        return (valInt >> 7,  (valInt >>  2) & 0x1F,  valInt & 0x3)
    if numberType == "fp16":
        return (valInt >> 15, (valInt >> 10) & 0x1F,  valInt & 0x3FF)
    if numberType == "bf16":
        return (valInt >> 15, (valInt >>  7) & 0xFF,  valInt & 0x7F)
    if numberType == "fp32":
        return (valInt >> 31, (valInt >> 23) & 0xFF,  valInt & 0x7FFFFF)
    if numberType == "fp64":
        return (valInt >> 63, (valInt >> 52) & 0x7FF, valInt & 0xFFFFFFFFFFFFF)

def toBitString(field, bitlength):
    resultArray = []
    for i in range(bitlength-1, -1, -1):
        bit = (field >> i) & 0x1
        resultArray.append(str(bit))
    return ''.join(resultArray)

def getBinaryString(sign, exp, frac, numberType):
    if numberType == "bf8":
        expString = toBitString(exp, 5)
        fracString = toBitString(frac, 2)
    if numberType == "fp16":
        expString = toBitString(exp, 5)
        fracString = toBitString(frac, 10)
    if numberType == "bf16":
        expString = toBitString(exp, 8)
        fracString = toBitString(frac, 7)
    if numberType == "fp32":
        expString = toBitString(exp, 8)
        fracString = toBitString(frac, 23)
    if numberType == "fp64":
        expString = toBitString(exp, 11)
        fracString = toBitString(frac, 52)
    return ' '.join([str(sign), expString, fracString])

def getSignInfo(sign):
    if sign:
        return "Negative"
    return "Positive"

def getExponentInfo(exp, numberType):
    if numberType == "bf8" or numberType == "fp16":
        return ''.join([str(exp), " - 15 = ", str(exp - 15)])
    if numberType == "bf16" or numberType == "fp32":
        return ''.join([str(exp), " - 127 = ", str(exp - 127)])
    if numberType == "fp64":
        return ''.join([str(exp), " - 1023 = ", str(exp - 1023)])

def printHelp():
    print("\nUsage: ", sys.argv[0],
          "[--bf8 | --bf16 | --fp16 | --fp32 | --fp64] number\n",
                                                          file=sys.stderr)
    print("""Notes: 1. If number is a non-negative integer (decimal, hex, or
          binary) it is taken as the bit pattern representation of
          the floating point value.
       2. If number contains a decimal (or binary) point, it is
          taken as the desired value itself.
       3. Underscores can be inserted in number for readability.
       4. The special floating point values epsilon, inf, and nan
          are also supported.  Epsilon is defined as the smallest
          value of x such that 1.0 + x > 1.0.\n""",       file=sys.stderr)
    print("Examples:", sys.argv[0], "--fp16 0x4200",      file=sys.stderr)
    print("         ", sys.argv[0], "--fp16 0b0_10000_1000000000",
                                                          file=sys.stderr)
    print("         ", sys.argv[0], "--fp32 0x4040_0000", file=sys.stderr)
    print("         ", sys.argv[0], "--fp32 0x1.8p1",     file=sys.stderr)
    print("         ", sys.argv[0], "--fp32 3.0",         file=sys.stderr)
    print("         ", sys.argv[0], "--fp64 epsilon",     file=sys.stderr)
    print("         ", sys.argv[0], "--fp64 inf",         file=sys.stderr)
    print("         ", sys.argv[0], "--fp64 nan\n",       file=sys.stderr)

def main():
    if len(sys.argv) <= 1:
        printHelp()
        return
    numberType = "fp64"
    for arg in sys.argv[1:-1]:
        if arg in ["--bf8", "--bf16", "--fp16", "--fp32", "--fp64"]:
            numberType = arg[2:]
        else:
            print("Invalid argument:", arg, file=sys.stderr)
            return
    inputString = sys.argv[-1]
    valueInt, valueFloat = decodeString(inputString, numberType)
    if valueInt == None:
        print("Invalid", numberType, "number:", inputString, file=sys.stderr)
        return
    print("")
    print("  DecValue:", valueFloat)
    hexValueString = getHexValueString(valueFloat, numberType)
    print("  HexValue:", hexValueString)
    print("       Hex:", "0x{0:X}".format(valueInt))
    sign, exp, frac = crack(valueInt, numberType)
    printKey("       Key:", numberType)
    print("    Binary:", getBinaryString(sign, exp, frac, numberType))
    print("      Sign:", getSignInfo(sign))
    print("  Exponent:", getExponentInfo(exp, numberType))
    print("  Fraction:", "0x{0:X}".format(frac))
    print("")

if __name__ == '__main__':
    main()

