# Context for the function to implement

- **Language:** go
- **File:** `cobra.go`

## Imports / includes available in this file

```
import "fmt"
import "io"
import "reflect"
import "strconv"
import "strings"
import "text/template"
import "time"
import "unicode"
```

## Other functions defined in the same file (signatures only; you may call them)

```
AddTemplateFunc name string , tmplFunc interface { }
AddTemplateFuncs tmplFuncs template . FuncMap
Eq a interface { } , b interface { }
Gt a interface { } , b interface { }
OnInitialize y ... func
appendIfNotPresent s , stringToAppend string
rpad s string , padding int
stringInSlice a string , list [ ] string
tmpl w io . Writer , text string , data interface { }
trimRightSpace s string
```
