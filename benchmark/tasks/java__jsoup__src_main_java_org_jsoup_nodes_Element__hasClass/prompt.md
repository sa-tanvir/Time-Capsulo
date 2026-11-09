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

`Element.hasClass(className)` tells whether the element's `class` attribute contains a given class name. Matching is case-insensitive and class names in the attribute are separated by whitespace.

## 2. Functional requirements

Let `classAttr` be the value of the element's `class` attribute, looked up with a case-insensitive attribute name (so `CLASS="x"` counts); if the element has no `class` attribute, `classAttr` is the empty string. Let `len` be its length and `wantLen` the length of `className`.

1. If `classAttr` is empty, or `classAttr` is shorter than `className`, return `false`.
2. If both have the same length, return whether `className` equals `classAttr` ignoring case. (This is a whole-value comparison, so it can be true even if the value contains whitespace, e.g. class `"a b"` and query `"a b"`.)
3. Otherwise split `classAttr` into tokens: maximal runs of characters that are not whitespace, where whitespace is as defined by `Character.isWhitespace(char)` (space, tab, newline, form feed, carriage return and other Unicode separators; U+00A0 is not whitespace under that definition). Return `true` if some token has the same length as `className` and equals it ignoring case (character-wise case-insensitive comparison, as `String.regionMatches(true, ...)` / `equalsIgnoreCase` do); otherwise `false`.
4. An empty `className` therefore returns `false` in every case.

Partial matches never count: `"foo"` does not match class `"foobar"`, nor `"bar"`, nor `"foo-bar"`.

## 3. Input specification

`className`: a non-null string, any content. The element may have any attributes; `class` may be missing, empty, padded with whitespace, or contain very long lists of names (tens of thousands of characters).

## 4. Output specification

A `boolean`. Examples:
- class `"foo bar"`: `hasClass("foo")` true, `hasClass("BAR")` true, `hasClass("fo")` false, `hasClass("baz")` false.
- class `"\tfoo\nbar\f"` (tabs/newlines as separators): `hasClass("bar")` true.
- class `"  foo  "`: `hasClass("foo")` true.
- class `"foobar foo"`: `hasClass("foo")` true; `hasClass("oo")` false.
- class `"École x"`: `hasClass("école")` true.
- no class attribute: `hasClass("foo")` false.

## 5. Edge cases and constraints

- The element is not modified. It is called in loops over large documents.
- Attribute-name case folding applies to the lookup of `class`; class-name comparison is case-insensitive, with no locale dependence.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/jsoup/nodes/Element.java`
- **Enclosing scope:** `public class Element extends Node`

## Imports / includes available in this file

```
import org.jsoup.helper.ChangeNotifyingArrayList;
import org.jsoup.helper.Validate;
import org.jsoup.internal.StringUtil;
import org.jsoup.parser.ParseSettings;
import org.jsoup.parser.Tag;
import org.jsoup.select.Collector;
import org.jsoup.select.Elements;
import org.jsoup.select.Evaluator;
import org.jsoup.select.NodeTraversor;
import org.jsoup.select.NodeVisitor;
import org.jsoup.select.QueryParser;
import org.jsoup.select.Selector;
import java.io.IOException;
import java.lang.ref.WeakReference;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;
import static org.jsoup.internal.Normalizer.normalize;
```

## Other functions defined in the same file (signatures only; you may call them)

```
Element::Element( String tag)
Element::Element( Tag tag , String baseUri , Attributes attributes)
Element::Element( Tag tag , String baseUri)
Element::NodeList::NodeList( Element owner , int initialCapacity)
Element::NodeList::onContentsChanged()
Element::accumulateParents( Element el , Elements parents)
Element::addClass( String className)
Element::after( Node node)
Element::after( String html)
Element::append( String html)
Element::appendChild( Node child)
Element::appendElement( String tagName)
Element::appendNormalisedText( StringBuilder accum , TextNode textNode)
Element::appendText( String text)
Element::appendTo( Element parent)
Element::appendWhitespaceIfBr( Element element , StringBuilder accum)
Element::attr( String attributeKey , String attributeValue)
Element::attr( String attributeKey , boolean attributeValue)
Element::attributes()
Element::baseUri()
Element::before( Node node)
Element::before( String html)
Element::child( int index)
Element::childElementsList()
Element::childNodeSize()
Element::children()
Element::className()
Element::classNames( Set<String> classNames)
Element::classNames()
Element::clone()
Element::cssSelector()
Element::data()
Element::dataNodes()
Element::dataset()
Element::doClone( Node parent)
Element::doSetBaseUri( String baseUri)
Element::elementSiblingIndex()
Element::empty()
Element::ensureChildNodes()
Element::firstElementSibling()
Element::getAllElements()
Element::getElementById( String id)
Element::getElementsByAttribute( String key)
Element::getElementsByAttributeStarting( String keyPrefix)
Element::getElementsByAttributeValue( String key , String value)
Element::getElementsByAttributeValueContaining( String key , String match)
Element::getElementsByAttributeValueEnding( String key , String valueSuffix)
Element::getElementsByAttributeValueMatching( String key , Pattern pattern)
Element::getElementsByAttributeValueMatching( String key , String regex)
Element::getElementsByAttributeValueNot( String key , String value)
Element::getElementsByAttributeValueStarting( String key , String valuePrefix)
Element::getElementsByClass( String className)
Element::getElementsByIndexEquals( int index)
Element::getElementsByIndexGreaterThan( int index)
Element::getElementsByIndexLessThan( int index)
Element::getElementsByTag( String tagName)
Element::getElementsContainingOwnText( String searchText)
Element::getElementsContainingText( String searchText)
Element::getElementsMatchingOwnText( Pattern pattern)
Element::getElementsMatchingOwnText( String regex)
Element::getElementsMatchingText( Pattern pattern)
Element::getElementsMatchingText( String regex)
Element::hasAttributes()
Element::hasText()
Element::html( String html)
Element::html( T appendable)
Element::html()
Element::id()
Element::indexInList( Element search , List<E> elements)
Element::insertChildren( int index , Collection <? extends Node> children)
Element::insertChildren( int index , Node ... children)
Element::is( Evaluator evaluator)
Element::is( String cssQuery)
Element::isBlock()
Element::lastElementSibling()
Element::nextElementSibling()
Element::nextElementSiblings( boolean next)
Element::nextElementSiblings()
Element::nodeName()
Element::nodelistChanged()
Element::normalName()
Element::outerHtmlHead( final Appendable accum , int depth , final Document . OutputSettings out)
Element::outerHtmlTail( Appendable accum , int depth , Document . OutputSettings out)
Element::ownText( StringBuilder accum)
Element::ownText()
Element::parent()
Element::parents()
Element::prepend( String html)
Element::prependChild( Node child)
Element::prependElement( String tagName)
Element::prependText( String text)
Element::preserveWhitespace( Node node)
Element::previousElementSibling()
Element::previousElementSiblings()
Element::removeClass( String className)
Element::select( String cssQuery)
Element::selectFirst( String cssQuery)
Element::shallowClone()
Element::siblingElements()
Element::tag()
Element::tagName( String tagName)
Element::tagName()
Element::text( String text)
Element::text()
Element::textNodes()
Element::toggleClass( String className)
Element::val( String value)
Element::val()
Element::wholeText()
Element::wrap( String html)
```

## Instance state

`Element` is a node with a tag, a child list and attributes. The method reads only:

- `attributes()` (`Attributes`, never null): the element's attribute collection. `Attributes.getIgnoreCase(String key)` returns the value of the attribute whose name equals `key` ignoring case, or the empty string `""` if there is none.

No other field is read or written. `hasClass` is public and takes the class name as given (no trimming or lower-casing is done by callers).

=== STUB ===
```java
public boolean hasClass(String className) {
    // TODO: implement according to the specification
}
```
