# Context for the function to implement

- **Language:** go
- **File:** `doc/rest_docs.go`

## Imports / includes available in this file

```
import "bytes"
import "fmt"
import "io"
import "os"
import "path/filepath"
import "sort"
import "strings"
import "time"
import "github.com/spf13/cobra"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(c*cobra.Command)
(s string)string
GenReST cmd * cobra . Command , w io . Writer
GenReSTCustom cmd * cobra . Command , w io . Writer , linkHandler func string , string string
GenReSTTreeCustom cmd * cobra . Command , dir string , filePrepender func string string , linkHandler func string , string string
defaultLinkHandler name , ref string
printOptionsReST buf * bytes . Buffer , cmd * cobra . Command , name string
```
