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

`looksLikeUtf8(input)` is a heuristic check used when decoding HTTP header values: it decides whether a byte array is plausibly UTF-8 encoded text. It is a structural check (lead and continuation bytes), not a full validator.

## 2. Functional requirements

Treat each byte as unsigned (0..255).

1. If the array starts with the three bytes `EF BB BF` (UTF-8 byte order mark), skip them and examine the rest.
2. Scan the remaining bytes from left to right:
   - A byte below `0x80` (high bit clear) is ASCII and acceptable on its own.
   - A byte of the form `110xxxxx` starts a 2-byte sequence (one continuation byte follows); `1110xxxx` starts a 3-byte sequence (two continuation bytes); `11110xxx` starts a 4-byte sequence (three continuation bytes).
   - Any other byte with the high bit set in a leading position (a stray continuation byte `10xxxxxx`, or `11111xxx` such as `0xF8..0xFF`) makes the result `false`.
   - For a sequence with `k` continuation bytes starting at index `i`, the array must have those `k` bytes after position `i`, and the last of them must not be the final byte of the array: if the index of the last continuation byte (`i + k`) is `>=` the array length, the result is `false`. Note that this means a multi-byte sequence ending exactly at the end of the array is accepted, but one that would run past the end is rejected.
   - Every continuation byte must have the form `10xxxxxx`, otherwise `false`.
   - After a complete sequence, scanning resumes at the byte after it.
3. If the whole array is scanned without failure, return `true`. An empty array, a BOM alone, and pure ASCII all return `true`.

The check does not reject overlong encodings, surrogate code points or values above U+10FFFF as long as lead/continuation structure is right.

## 3. Input specification

`input`: a non-null `byte[]` of any length from 0 up to several hundred thousand bytes.

## 4. Output specification

A `boolean`. Examples: `{}` true; `{0x41}` true; `{0xC3, 0xA9}` true; `{0xC3}` false; `{0xC3, 0x28}` false; `{0xE2, 0x82, 0xAC}` true; `{0xE2, 0x82}` false; `{0xF0, 0x9F, 0x98, 0x80}` true; `{0xFF}` false; `{0x80}` false; `{0xEF, 0xBB, 0xBF, 0x41}` true; `{0xEF, 0xBB}` false (the first byte `0xEF` begins a 3-byte sequence that is cut off); `{0xEF, 0xBB, 0xBF, 0xC3}` false; `{0x63, 0x61, 0x66, 0xE9}` false (a Latin-1 string).

## 5. Edge cases and constraints

- The array is not modified. The method has no side effects and is a pure function of its argument.
- Must make a single pass; it is applied to large arrays.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/jsoup/helper/HttpConnection.java`
- **Enclosing scope:** `public class HttpConnection implements Connection`

## Imports / includes available in this file

```
import org.jsoup.Connection;
import org.jsoup.HttpStatusException;
import org.jsoup.UncheckedIOException;
import org.jsoup.UnsupportedMimeTypeException;
import org.jsoup.internal.ConstrainableInputStream;
import org.jsoup.internal.StringUtil;
import org.jsoup.nodes.Document;
import org.jsoup.parser.Parser;
import org.jsoup.parser.TokenQueue;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLSocketFactory;
import java.io.BufferedInputStream;
import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.net.MalformedURLException;
import java.net.Proxy;
import java.net.URI;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.Buffer;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.nio.charset.IllegalCharsetNameException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.zip.GZIPInputStream;
import java.util.zip.Inflater;
import java.util.zip.InflaterInputStream;
import static org.jsoup.Connection.Method.HEAD;
import static org.jsoup.internal.Normalizer.lowerCase;
```

## Other functions defined in the same file (signatures only; you may call them)

```
HttpConnection::Base::Base()
HttpConnection::Base::addHeader( String name , String value)
HttpConnection::Base::cookie( String name , String value)
HttpConnection::Base::cookie( String name)
HttpConnection::Base::cookies()
HttpConnection::Base::fixHeaderEncoding( String val)
HttpConnection::Base::getHeadersCaseInsensitive( String name)
HttpConnection::Base::hasCookie( String name)
HttpConnection::Base::hasHeader( String name)
HttpConnection::Base::hasHeaderWithValue( String name , String value)
HttpConnection::Base::header( String name , String value)
HttpConnection::Base::header( String name)
HttpConnection::Base::headers( String name)
HttpConnection::Base::headers()
HttpConnection::Base::method( Method method)
HttpConnection::Base::method()
HttpConnection::Base::multiHeaders()
HttpConnection::Base::removeCookie( String name)
HttpConnection::Base::removeHeader( String name)
HttpConnection::Base::scanHeaders( String name)
HttpConnection::Base::url( URL url)
HttpConnection::Base::url()
HttpConnection::HttpConnection()
HttpConnection::KeyVal::KeyVal()
HttpConnection::KeyVal::contentType( String contentType)
HttpConnection::KeyVal::contentType()
HttpConnection::KeyVal::create( String key , String filename , InputStream stream)
HttpConnection::KeyVal::create( String key , String value)
HttpConnection::KeyVal::hasInputStream()
HttpConnection::KeyVal::inputStream( InputStream inputStream)
HttpConnection::KeyVal::inputStream()
HttpConnection::KeyVal::key( String key)
HttpConnection::KeyVal::key()
HttpConnection::KeyVal::toString()
HttpConnection::KeyVal::value( String value)
HttpConnection::KeyVal::value()
HttpConnection::Request::Request()
HttpConnection::Request::data( Connection . KeyVal keyval)
HttpConnection::Request::data()
HttpConnection::Request::followRedirects( boolean followRedirects)
HttpConnection::Request::followRedirects()
HttpConnection::Request::ignoreContentType( boolean ignoreContentType)
HttpConnection::Request::ignoreContentType()
HttpConnection::Request::ignoreHttpErrors( boolean ignoreHttpErrors)
HttpConnection::Request::ignoreHttpErrors()
HttpConnection::Request::maxBodySize( int bytes)
HttpConnection::Request::maxBodySize()
HttpConnection::Request::parser( Parser parser)
HttpConnection::Request::parser()
HttpConnection::Request::postDataCharset( String charset)
HttpConnection::Request::postDataCharset()
HttpConnection::Request::proxy( Proxy proxy)
HttpConnection::Request::proxy( String host , int port)
HttpConnection::Request::proxy()
HttpConnection::Request::requestBody( String body)
HttpConnection::Request::requestBody()
HttpConnection::Request::sslSocketFactory( SSLSocketFactory sslSocketFactory)
HttpConnection::Request::sslSocketFactory()
HttpConnection::Request::timeout( int millis)
HttpConnection::Request::timeout()
HttpConnection::Response::Response( Response previousResponse)
HttpConnection::Response::Response()
HttpConnection::Response::body()
HttpConnection::Response::bodyAsBytes()
HttpConnection::Response::bodyStream()
HttpConnection::Response::bufferUp()
HttpConnection::Response::charset( String charset)
HttpConnection::Response::charset()
HttpConnection::Response::contentType()
HttpConnection::Response::createConnection( Connection . Request req)
HttpConnection::Response::createHeaderMap( HttpURLConnection conn)
HttpConnection::Response::execute( Connection . Request req , Response previousResponse)
HttpConnection::Response::execute( Connection . Request req)
HttpConnection::Response::getRequestCookieString( Connection . Request req)
HttpConnection::Response::parse()
HttpConnection::Response::prepareByteData()
HttpConnection::Response::processResponseHeaders( Map<String,List<String>> resHeaders)
HttpConnection::Response::safeClose()
HttpConnection::Response::serialiseRequestUrl( Connection . Request req)
HttpConnection::Response::setOutputContentType( final Connection . Request req)
HttpConnection::Response::setupFromConnection( HttpURLConnection conn , HttpConnection . Response previousResponse)
HttpConnection::Response::statusCode()
HttpConnection::Response::statusMessage()
HttpConnection::Response::writePost( final Connection . Request req , final OutputStream outputStream , final String bound)
HttpConnection::connect( String url)
HttpConnection::connect( URL url)
HttpConnection::cookie( String name , String value)
HttpConnection::cookies( Map<String,String> cookies)
HttpConnection::data( Collection<Connection.KeyVal> data)
HttpConnection::data( Map<String,String> data)
HttpConnection::data( String ... keyvals)
HttpConnection::data( String key , String filename , InputStream inputStream , String contentType)
HttpConnection::data( String key , String filename , InputStream inputStream)
HttpConnection::data( String key , String value)
HttpConnection::data( String key)
HttpConnection::encodeMimeName( String val)
HttpConnection::encodeUrl( String url)
HttpConnection::encodeUrl( URL u)
HttpConnection::execute()
HttpConnection::followRedirects( boolean followRedirects)
HttpConnection::get()
HttpConnection::header( String name , String value)
HttpConnection::headers( Map<String,String> headers)
HttpConnection::ignoreContentType( boolean ignoreContentType)
HttpConnection::ignoreHttpErrors( boolean ignoreHttpErrors)
HttpConnection::maxBodySize( int bytes)
HttpConnection::method( Method method)
HttpConnection::needsMultipart( Connection . Request req)
HttpConnection::parser( Parser parser)
HttpConnection::post()
HttpConnection::postDataCharset( String charset)
HttpConnection::proxy( Proxy proxy)
HttpConnection::proxy( String host , int port)
HttpConnection::referrer( String referrer)
HttpConnection::request( Connection . Request request)
HttpConnection::request()
HttpConnection::requestBody( String body)
HttpConnection::response( Connection . Response response)
HttpConnection::response()
HttpConnection::sslSocketFactory( SSLSocketFactory sslSocketFactory)
HttpConnection::timeout( int millis)
HttpConnection::url( String url)
HttpConnection::url( URL url)
HttpConnection::userAgent( String userAgent)
```

## Instance state

`looksLikeUtf8` is a `private static` method of the nested class `HttpConnection.Base` (the common base of the request and response objects); it is a pure function of its argument and reads no instance or static state. It is used by the private static `fixHeaderEncoding(String)` of the same class, which re-decodes an ISO-8859-1 header value as UTF-8 when `looksLikeUtf8` accepts the bytes.

=== STUB ===
```java
private static boolean looksLikeUtf8(byte[] input) {
    // TODO: implement according to the specification
}
```
