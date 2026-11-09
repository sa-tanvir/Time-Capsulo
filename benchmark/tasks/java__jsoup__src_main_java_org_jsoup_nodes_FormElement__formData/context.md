# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/jsoup/nodes/FormElement.java`
- **Enclosing scope:** `public class FormElement extends Element`

## Imports / includes available in this file

```
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.helper.HttpConnection;
import org.jsoup.helper.Validate;
import org.jsoup.parser.Tag;
import org.jsoup.select.Elements;
import java.util.ArrayList;
import java.util.List;
```

## Other functions defined in the same file (signatures only; you may call them)

```
FormElement::FormElement( Tag tag , String baseUri , Attributes attributes)
FormElement::addElement( Element element)
FormElement::elements()
FormElement::removeChild( Node out)
FormElement::submit()
```

## Instance state

Fields of `FormElement` (a subclass of `Element`) used by the method:

- `elements` (`Elements`, private final, an `ArrayList<Element>` subclass): the form controls associated with this form (filled by the parser as it meets controls inside the form, and by `addElement`), in document order. Includes controls of any tag, e.g. `input`, `button`, `select`, `textarea`, `object`, `keygen`.

Methods read on each control `el` (an `Element`): `el.tag().isFormSubmittable()` (true for tags `input`, `keygen`, `object`, `select`, `textarea`), `el.hasAttr(String)`, `el.attr(String)` (empty string if absent), `el.tagName()`, `el.val()` (see the specification), `el.select(String cssQuery)` returning `Elements` (e.g. `option[selected]`, `option`) and `Elements.first()` (null if empty). `HttpConnection.KeyVal.create(String key, String value)` creates a pair (the key must be non-empty).
