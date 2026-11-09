# Third-party code

Each task contains code taken from an open-source library: the original function (`reference.*`), excerpts in `context.md`, and the libraries' test configuration.
That code remains under its library's licence, listed below. The full licence text, and the NOTICE file where the library ships one, is included in `third_party_licenses/<language>__<library>/` for each of the 30 libraries (copied from the pinned version, commit as in the table). `setup.sh` also downloads the whole library into `repos/`. Contributor lists (AUTHORS files) are not copied here; they are in each library's repository. Email addresses that appear inside the licence texts are part of the original copyright notices and are kept unchanged.

| Language | Library | Version | Licence | Source |
|---|---|---|---|---|
| python | requests | v2.22.0 | Apache-2.0 | https://github.com/psf/requests (commit `aeda65bbe57a`) |
| python | click | 7.0 | BSD-3-Clause | https://github.com/pallets/click (commit `a936b99212c6`) |
| python | more-itertools | v7.2.0 | MIT | https://github.com/more-itertools/more-itertools (commit `99884cbd7f78`) |
| python | python-sortedcontainers | v2.1.0 | Apache-2.0 | https://github.com/grantjenks/python-sortedcontainers (commit `e05634b0f0b8`) |
| python | dateutil | 2.8.1 | Apache-2.0 AND BSD-3-Clause | https://github.com/dateutil/dateutil (commit `fc9b1625ebc7`) |
| go | go-humanize | v1.0.0 | MIT | https://github.com/dustin/go-humanize (commit `9f541cc9db5d`) |
| go | semver | v3.0.3 | MIT | https://github.com/Masterminds/semver (commit `910aa146bd66`) |
| go | mux | v1.7.0 | BSD-3-Clause | https://github.com/gorilla/mux (commit `a7962380ca08`) |
| go | gjson | v1.3.5 | MIT | https://github.com/tidwall/gjson (commit `5c2e4b382486`) |
| go | cobra | v0.0.5 | Apache-2.0 | https://github.com/spf13/cobra (commit `f2b07da1e2c3`) |
| javascript | qs | v6.9.1 | BSD-3-Clause | https://github.com/ljharb/qs (commit `7b368004723b`) |
| javascript | node-semver | v6.3.0 | ISC | https://github.com/npm/node-semver (commit `0eeceecfba49`) |
| javascript | validator.js | 12.1.0 | MIT | https://github.com/validatorjs/validator.js (commit `0d204da14f64`) |
| javascript | lodash | 4.17.14 | MIT | https://github.com/lodash/lodash (commit `be87d3039412`) |
| javascript | moment | 2.24.0 | MIT | https://github.com/moment/moment (commit `96d0d6791ab4`) |
| rust | strsim-rs | 0.9.2 | MIT | https://github.com/dguo/strsim-rs (commit `cc25041cc1aa`) |
| rust | textwrap | 0.11.0 | MIT | https://github.com/mgeisler/textwrap (commit `abcd618beae3`) |
| rust | rust-base64 | v0.11.0 | MIT OR Apache-2.0 | https://github.com/marshallpierce/rust-base64 (commit `edc3859d8300`) |
| rust | clap | v2.30.0 | MIT | https://github.com/clap-rs/clap (commit `ebe14558e65e`) |
| rust | regex | 1.0.0 | MIT OR Apache-2.0 | https://github.com/rust-lang/regex (commit `b5ef0ec28122`) |
| java | commons-codec | commons-codec-1.13 | Apache-2.0 | https://github.com/apache/commons-codec (commit `beafa49f88be`) |
| java | commons-text | commons-text-1.8 | Apache-2.0 | https://github.com/apache/commons-text (commit `b63df8d66e83`) |
| java | jsoup | jsoup-1.12.1 | MIT | https://github.com/jhy/jsoup (commit `3f0256953a29`) |
| java | commons-lang | commons-lang-3.9 | Apache-2.0 | https://github.com/apache/commons-lang (commit `abb39c22c0e5`) |
| java | gson | gson-parent-2.8.6 | Apache-2.0 | https://github.com/google/gson (commit `29c93895bbca`) |
| cpp | pugixml | v1.10 | MIT | https://github.com/zeux/pugixml (commit `3c59df555b93`) |
| cpp | fmt | 6.1.0 | MIT | https://github.com/fmtlib/fmt (commit `4ca6821e8f26`) |
| cpp | double-conversion | v3.1.5 | BSD-3-Clause | https://github.com/google/double-conversion (commit `5fa81e88ef24`) |
| cpp | spdlog | v1.3.1 | MIT | https://github.com/gabime/spdlog (commit `a7148b718ea2`) |
| cpp | json | v3.7.2 | MIT | https://github.com/nlohmann/json (commit `411158d896c8`) |

## Changes made to the library code

- `stub.*` and the stub inside `prompt.md` are the original file with the body of one function removed.
- `context.md` and `prompt.md` contain excerpts of the original files, selected and in places shortened or annotated (for example to mark undocumented internals). Excerpts are not complete files.
- `reference.*` is the original function, unchanged.
- The libraries' build and test configuration was adapted (benchmark/repos/) to run their own tests in Docker.
- The Apache-2.0 libraries (requests, python-sortedcontainers, dateutil, cobra, commons-codec, commons-text, commons-lang, gson, and rust-base64 and regex where used under Apache-2.0) require that changes be stated: this section is that statement. Their NOTICE files, where they exist (commons-codec, commons-text, commons-lang), are in `third_party_licenses/`.
- The BSD-3-Clause libraries (click, mux, qs, double-conversion, and the BSD part of dateutil): the names of the libraries' authors and contributors are not used to endorse or promote Time Capsulo or any result obtained with it.

## Licence of Time Capsulo itself

The specifications, workloads, benchmark drivers, harness and documentation were written for Time Capsulo. Code is under the MIT License and data and documentation are under CC BY 4.0, as set out in `LICENSE` and `LICENSE-DATA-CC-BY-4.0.txt`. Neither licence applies to the third-party code listed above.
