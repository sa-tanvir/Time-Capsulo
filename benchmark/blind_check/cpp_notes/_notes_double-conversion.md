AssignPowerUInt16: none (assumed Square/MultiplyByUInt32/ShiftLeft work on a value with exponent_; uncertain whether the hidden original used a faster bit-trick, but spec allows any exact method)
PlusCompare: none significant (had to infer that BigitLength/BigitAt are usable on the const refs and that zero has exponent 0; no complexity bound beyond "proportional to digits" - my loop goes from the lowest exponent, which may be large if operand exponents differ widely)
GenerateShortestDigits: none (spec algorithm is explicit; the 'is_even' boundary conditions and tie rule are clear)
IsHexFloatString: mildly unclear: separator "digit" in the exponent is stated as hex digit, so I used base 16 for Advance there; behavior of "1p1_a" (skipping into a non-decimal hex digit) is a guess consistent with the table
RadixStringToIeee: several guesses: (a) hex-float with fractional digits plus overflow rounding exponent bookkeeping, (b) clamping huge exponents to +-5000 before Double(DiyFp), relying on Double(DiyFp) to give infinity/0 and to accept non-normalized significands, (c) the junk check placement for leading-zero-only text with trailing junk e.g. "0z" interpreted via the normal digit loop, (d) '.' stepping with separators in hex-float tail not specified, (e) behaviour when sign true and result is zero after junk-allowed stop assumed -0.0
ToExponential: none
ToPrecision: none (buffer capacity for DoubleToAscii not stated; I assumed precision+1 is enough)
RoundWeed: none
RoundWeedCounted: none
FillFractionals: UB when point reaches 0 (exponent 0) not addressed in spec; I guarded the rounding bit test with point > 0; overflow safety of 64-bit path for exponent near -64 assumed from the stated input bound (fractionals < 2^53)
