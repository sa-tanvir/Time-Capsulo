# Context for the function to implement

- **Language:** go
- **File:** `bigbytes.go`

## Imports / includes available in this file

```
import "fmt"
import "math/big"
import "strings"
import "unicode"
```

## Other functions defined in the same file (signatures only; you may call them)

```
BigBytes s * big . Int
BigIBytes s * big . Int
humanateBigBytes s , base * big . Int , sizes [ ] string
```

## Package-level variables defined in this file (you may use them)

```go
var (
	bigIECExp = big.NewInt(1024)

	// BigByte is one byte in bit.Ints
	BigByte = big.NewInt(1)
	// BigKiByte is 1,024 bytes in bit.Ints
	BigKiByte = (&big.Int{}).Mul(BigByte, bigIECExp)
	// BigMiByte is 1,024 k bytes in bit.Ints
	BigMiByte = (&big.Int{}).Mul(BigKiByte, bigIECExp)
	// BigGiByte is 1,024 m bytes in bit.Ints
	BigGiByte = (&big.Int{}).Mul(BigMiByte, bigIECExp)
	// BigTiByte is 1,024 g bytes in bit.Ints
	BigTiByte = (&big.Int{}).Mul(BigGiByte, bigIECExp)
	// BigPiByte is 1,024 t bytes in bit.Ints
	BigPiByte = (&big.Int{}).Mul(BigTiByte, bigIECExp)
	// BigEiByte is 1,024 p bytes in bit.Ints
	BigEiByte = (&big.Int{}).Mul(BigPiByte, bigIECExp)
	// BigZiByte is 1,024 e bytes in bit.Ints
	BigZiByte = (&big.Int{}).Mul(BigEiByte, bigIECExp)
	// BigYiByte is 1,024 z bytes in bit.Ints
	BigYiByte = (&big.Int{}).Mul(BigZiByte, bigIECExp)
)

var (
	bigSIExp = big.NewInt(1000)

	// BigSIByte is one SI byte in big.Ints
	BigSIByte = big.NewInt(1)
	// BigKByte is 1,000 SI bytes in big.Ints
	BigKByte = (&big.Int{}).Mul(BigSIByte, bigSIExp)
	// BigMByte is 1,000 SI k bytes in big.Ints
	BigMByte = (&big.Int{}).Mul(BigKByte, bigSIExp)
	// BigGByte is 1,000 SI m bytes in big.Ints
	BigGByte = (&big.Int{}).Mul(BigMByte, bigSIExp)
	// BigTByte is 1,000 SI g bytes in big.Ints
	BigTByte = (&big.Int{}).Mul(BigGByte, bigSIExp)
	// BigPByte is 1,000 SI t bytes in big.Ints
	BigPByte = (&big.Int{}).Mul(BigTByte, bigSIExp)
	// BigEByte is 1,000 SI p bytes in big.Ints
	BigEByte = (&big.Int{}).Mul(BigPByte, bigSIExp)
	// BigZByte is 1,000 SI e bytes in big.Ints
	BigZByte = (&big.Int{}).Mul(BigEByte, bigSIExp)
	// BigYByte is 1,000 SI z bytes in big.Ints
	BigYByte = (&big.Int{}).Mul(BigZByte, bigSIExp)
)

var bigBytesSizeTable = map[string]*big.Int{
	"b":   BigByte,
	"kib": BigKiByte,
	"kb":  BigKByte,
	"mib": BigMiByte,
	"mb":  BigMByte,
	"gib": BigGiByte,
	"gb":  BigGByte,
	"tib": BigTiByte,
	"tb":  BigTByte,
	"pib": BigPiByte,
	"pb":  BigPByte,
	"eib": BigEiByte,
	"eb":  BigEByte,
	"zib": BigZiByte,
	"zb":  BigZByte,
	"yib": BigYiByte,
	"yb":  BigYByte,
	// Without suffix
	"":   BigByte,
	"ki": BigKiByte,
	"k":  BigKByte,
	"mi": BigMiByte,
	"m":  BigMByte,
	"gi": BigGiByte,
	"g":  BigGByte,
	"ti": BigTiByte,
	"t":  BigTByte,
	"pi": BigPiByte,
	"p":  BigPByte,
	"ei": BigEiByte,
	"e":  BigEByte,
	"z":  BigZByte,
	"zi": BigZiByte,
	"y":  BigYByte,
	"yi": BigYiByte,
}

var ten = big.NewInt(10)
```
