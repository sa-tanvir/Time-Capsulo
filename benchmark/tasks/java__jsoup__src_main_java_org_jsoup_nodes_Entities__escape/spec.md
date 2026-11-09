# Functional specification

## 1. Component overview

`Entities.escape(accum, string, out, inAttribute, normaliseWhite, stripLeadingWhite)` writes an HTML/XML-escaped form of `string` to `accum`, according to the output settings `out` (character set and entity set). It is the core of jsoup's text and attribute serialisation.

## 2. Functional requirements

Walk `string` by Unicode code point (a surrogate pair is one code point) and append to `accum` for each one, in order:

1. **Whitespace normalisation (only if `normaliseWhite` is true).** The whitespace code points here are space, tab, line feed, form feed and carriage return (`StringUtil.isWhitespace(int)`; U+00A0 is not one of them). A whitespace code point is dropped if `stripLeadingWhite` is true and no non-whitespace code point has been processed yet, or if the previously processed code point was whitespace; otherwise a single `' '` is appended. Whitespace handling is finished for that code point (it is never escaped further). Every non-whitespace code point resets the "previous was whitespace" state and marks that content has started. If `normaliseWhite` is false, whitespace is treated like any other character.
2. **Required escapes (code points below U+10000):**
   - `&` becomes `&amp;`.
   - U+00A0 becomes `&nbsp;`, except when `out.escapeMode()` is `xhtml`, where it becomes `&#xa0;`.
   - `<` becomes `&lt;`, except that it is written literally when `inAttribute` is true and the mode is not `xhtml`.
   - `>` becomes `&gt;`, except that it is written literally when `inAttribute` is true.
   - `"` becomes `&quot;` only when `inAttribute` is true; otherwise it is written literally.
3. **Any other code point:** if the output charset (`out.encoder()`) can encode it, append it unchanged. Otherwise append its entity: `&name;` using the name that the current escape mode (`out.escapeMode()`) defines for that code point if there is one, else a numeric reference `&#x<hex>;` with lower-case hexadecimal digits and no leading zeros. This applies to supplementary code points too (they are encodable by the Unicode charsets, so they appear literally there; under US-ASCII or ISO-8859-1 they are written as entities).
4. The `xhtml` mode has names only for the four basic characters; `base` has a medium-sized set and `extended` the full HTML set, so the same code point can be a named entity in one mode and numeric in another (for example U+00E9 in US-ASCII output).

## 3. Input specification

`accum`: any `Appendable`. `string`: non-null, may be empty, may contain any well-formed Unicode text. `out`: a `Document.OutputSettings` whose charset is, for example, UTF-8, US-ASCII or ISO-8859-1, and whose mode is `xhtml`, `base` or `extended`. Three booleans as above.

## 4. Output specification

Returns nothing; throws `IOException` only if `accum` does. Examples (UTF-8, `base`, `inAttribute=false`, no normalisation): `a<b>&"c"` gives `a&lt;b&gt;&amp;"c"`; with `inAttribute=true` it gives `a<b>&amp;&quot;c&quot;`. US-ASCII, `base`: `café` gives `caf&eacute;`; `中` gives `&#x4e2d;`. With normalisation and strip-leading: `"  a \n\t b "` gives `a b `.

## 5. Edge cases and constraints

- Empty input appends nothing. Output depends only on the arguments; no locale dependence.
- Characters are appended one run at a time to `accum`; do not build the whole result in an intermediate structure of unbounded size beyond what is needed (inputs can have hundreds of thousands of characters).
