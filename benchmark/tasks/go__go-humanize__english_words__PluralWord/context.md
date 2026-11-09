# Context for the function to implement

- **Language:** go
- **File:** `english/words.go`

## Imports / includes available in this file

```
import "fmt"
import "strings"
import humanize "github.com/dustin/go-humanize"
```

## Other functions defined in the same file (signatures only; you may call them)

```
OxfordWordSeries words [ ] string , conjunction string
Plural quantity int , singular , plural string
WordSeries words [ ] string , conjunction string
```

## Package-level variables defined in this file (you may use them)

```go
// These are included because they are common technical terms.
var specialPlurals = map[string]string{
	"index":  "indices",
	"matrix": "matrices",
	"vertex": "vertices",
}

var sibilantEndings = []string{"s", "sh", "tch", "x"}

var isVowel = map[byte]bool{
	'A': true, 'E': true, 'I': true, 'O': true, 'U': true,
	'a': true, 'e': true, 'i': true, 'o': true, 'u': true,
}
```
