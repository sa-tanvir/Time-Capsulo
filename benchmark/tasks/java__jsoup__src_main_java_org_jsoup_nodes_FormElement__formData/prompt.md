You are an expert Java developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Java code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```java code block, with no explanation.

=== SPECIFICATION ===
# Functional specification

## 1. Component overview

`FormElement.formData()` returns the name/value pairs that a browser would submit for an HTML `<form>`, based on the form controls associated with the form element.

## 2. Functional requirements

Iterate over the form's associated controls (the `elements` collection, in document order) and build a new list of key/value pairs (`Connection.KeyVal`, created with `HttpConnection.KeyVal.create(name, value)`). For each control `el`:

1. Skip it if its tag is not form-submittable. The submittable tags are `input`, `keygen`, `object`, `select` and `textarea` (`el.tag().isFormSubmittable()`); for example `button` is skipped.
2. Skip it if it has a `disabled` attribute (present with any value, including empty).
3. Let `name` be its `name` attribute (empty string if absent). Skip the control if `name` is empty.
4. If the tag is `select`: take all `option` descendants that have a `selected` attribute, in document order, and add one pair `(name, option.val())` for each. If none is selected, add one pair for the first `option` descendant (if the select has no options, add nothing).
5. Else if the control's `type` attribute equals `checkbox` or `radio` (ignoring case): add a pair only if the control has a `checked` attribute; the value is `el.val()` if that is non-empty, else the string `on`.
6. Otherwise (text, hidden, password, submit, file, textarea, keygen, no type, any other type): add `(name, el.val())`, including the empty value.

`Element.val()` is the control's text content for a `textarea`, and the value of its `value` attribute (empty string if absent) for everything else, including `option`.

## 3. Input specification

The form is part of a parsed document; `elements` holds the controls that were linked to the form during parsing (inputs nested in other elements inside the form are included). The form can have from none up to tens of thousands of controls.

## 4. Output specification

A new `List<Connection.KeyVal>` (an `ArrayList`); modifying it does not affect the document. Pairs appear in control order, and for a multi-select in option order. Example: `<form><input name=a value=1><input name=b type=checkbox><input name=c type=checkbox checked><select name=s><option value=1>a<option value=2 selected>b</select><input name=e disabled value=x></form>` gives `a=1`, `c=on`, `s=2`.

## 5. Edge cases and constraints

- Controls without a name, disabled controls and unchecked checkboxes or radios contribute nothing. A `select` with no `selected` option contributes its first option's value. Nothing in the document is modified.
- Names and values are used as they are (no URL encoding).

=== CONTEXT ===
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

=== STUB ===
```java
public List<Connection.KeyVal> formData() {
    // TODO: implement according to the specification
}
```
