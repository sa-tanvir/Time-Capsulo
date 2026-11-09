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
