# fpDecoder
Decodes floating point constants

Note that everything needed is in one file, `fpDecoder.py`, so it is not
necessary to clone the git repository to use the decoder.

## Usage

Usage: `fpDecoder.py [--bf8 | --bf16 | --fp16 | --fp32 | --fp64] number`

Notes:
1. If `number` is a non-negative integer (decimal, hex, or
   binary) it is taken as the bit pattern representation of
   the floating point value.
2. If `number` contains a decimal (or binary) point, it is
   taken as the desired value itself.
3. Underscores can be inserted in `number` for readability.
4. The special floating point values `epsilon`, `inf`, and `nan`
   are also supported.  Epsilon is defined as the smallest
   value of x such that 1.0 + x > 1.0.

## Examples

`fpDecoder.py --fp16 0x4200`
```
  DecValue: 3.0
  HexValue: 0x1.800p+1
       Hex: 0x4200
       Key: 1       0
            5 43210 9876543210
            S -E5-- ---F10----
    Binary: 0 10000 1000000000
      Sign: Positive
  Exponent: 16 - 15 = 1
  Fraction: 0x200
```

`fpDecoder.py --fp16 0b0_10000_1000000000`
```
  DecValue: 3.0
  HexValue: 0x1.800p+1
       Hex: 0x4200
       Key: 1       0
            5 43210 9876543210
            S -E5-- ---F10----
    Binary: 0 10000 1000000000
      Sign: Positive
  Exponent: 16 - 15 = 1
  Fraction: 0x200
```

`fpDecoder.py --fp32 0x4040_0000`
```
  DecValue: 3.0
  HexValue: 0x1.800000p+1
       Hex: 0x40400000
       Key: 3  2          1         0
            1 09876543 21098765432109876543210
            S ---E8--- ----------F23----------
    Binary: 0 10000000 10000000000000000000000
      Sign: Positive
  Exponent: 128 - 127 = 1
  Fraction: 0x400000
```

`fpDecoder.py --fp32 0x1.8p1`
```
  DecValue: 3.0
  HexValue: 0x1.800000p+1
       Hex: 0x40400000
       Key: 3  2          1         0
            1 09876543 21098765432109876543210
            S ---E8--- ----------F23----------
    Binary: 0 10000000 10000000000000000000000
      Sign: Positive
  Exponent: 128 - 127 = 1
  Fraction: 0x400000
```

`fpDecoder.py --fp32 3.0`
```
  DecValue: 3.0
  HexValue: 0x1.800000p+1
       Hex: 0x40400000
       Key: 3  2          1         0
            1 09876543 21098765432109876543210
            S ---E8--- ----------F23----------
    Binary: 0 10000000 10000000000000000000000
      Sign: Positive
  Exponent: 128 - 127 = 1
  Fraction: 0x400000
```

`fpDecoder.py --fp64 epsilon`
```
  DecValue: 2.220446049250313e-16
  HexValue: 0x1.0000000000000p-52
       Hex: 0x3CB0000000000000
       Key: 6    5          4         3         2         1         0
            3 21098765432 1098765432109876543210987654321098765432109876543210
            S ----E11---- ------------------------F52-------------------------
    Binary: 0 01111001011 0000000000000000000000000000000000000000000000000000
      Sign: Positive
  Exponent: 971 - 1023 = -52
  Fraction: 0x0
```

`fpDecoder.py --fp64 inf`
```
  DecValue: inf
  HexValue: inf
       Hex: 0x7FF0000000000000
       Key: 6    5          4         3         2         1         0
            3 21098765432 1098765432109876543210987654321098765432109876543210
            S ----E11---- ------------------------F52-------------------------
    Binary: 0 11111111111 0000000000000000000000000000000000000000000000000000
      Sign: Positive
  Exponent: 2047 - 1023 = 1024
  Fraction: 0x0
```

`fpDecoder.py --fp64 nan`
```
  DecValue: nan
  HexValue: nan
       Hex: 0x7FF8000000000000
       Key: 6    5          4         3         2         1         0
            3 21098765432 1098765432109876543210987654321098765432109876543210
            S ----E11---- ------------------------F52-------------------------
    Binary: 0 11111111111 1000000000000000000000000000000000000000000000000000
      Sign: Positive
  Exponent: 2047 - 1023 = 1024
  Fraction: 0x8000000000000
```

