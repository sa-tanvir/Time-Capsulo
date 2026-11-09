#!/usr/bin/env bash
# One-time setup for the Time Capsulo benchmark (Python + Go + JavaScript + Rust + Java + C++ release).
# Requirements: Docker (running), Python 3.8+, internet access for this step only.
# Optional: ./setup.sh python | go | javascript | rust | java | cpp   to set up some languages only.
set -euo pipefail
cd "$(dirname "$0")"
LANGS=${*:-python go javascript rust java cpp}

echo "== 1/5 harness virtualenv"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt

echo "== 2/5 era toolchain images"
for l in $LANGS; do
  case $l in
    python) echo "   tc-python37 (Python 3.7 + pytest 5.3.5)"
            docker build -q -t tc-python37 -f harness/docker/python37.Dockerfile harness/docker ;;
    go)     echo "   tc-go (Go 1.13 + pinned goimports)"
            docker build -q -t tc-go -f harness/docker/go.Dockerfile harness/docker ;;
    javascript) echo "   tc-javascript (Node.js 10 + npm 6 + test-runner adapters)"
            docker build -q -t tc-javascript -f harness/docker/javascript.Dockerfile harness/docker ;;
    rust)   echo "   tc-rust (Rust 1.40, Dec 2019)"
            docker build -q -t tc-rust -f harness/docker/rust.Dockerfile harness/docker ;;
    java)   echo "   tc-java (Maven 3.6 + Amazon Corretto 8)"
            docker build -q -t tc-java -f harness/docker/java.Dockerfile harness/docker ;;
    cpp)    echo "   tc-cpp (GCC 9.4 + CMake 3.16, Ubuntu 20.04)"
            docker build -q -t tc-cpp -f harness/docker/cpp.Dockerfile harness/docker ;;
    *)      echo "unknown language: $l" >&2; exit 2 ;;
  esac
done

echo "== 3/5 measurement helper (static binary for this machine's architecture)"
docker run --rm -v "$PWD/harness/tools:/t" alpine:3.12@sha256:c75ac27b49326926b803b9ed43bf088bc220d22556de1bc5f72d742c91398f69 \
  sh -c "apk add -q --no-cache build-base && gcc -O2 -static -o /t/tcmeasure /t/tcmeasure.c"

echo "== 4/5 pinned 2018-2019 repository sources (verified by content hash)"
python3 harness/fetch_repos.py $LANGS

echo "== 5/5 per-repo working copies and pinned test dependencies"
for l in $LANGS; do
  for f in benchmark/repos/${l}__*.json; do
    case $f in *.baseline.json) continue ;; esac
    .venv/bin/python harness/tc.py setup "$(basename "$f" .json)"
  done
done
echo "Setup complete. Next: .venv/bin/python harness/tc.py check python__more-itertools__more_itertools_more__windowed"
echo "                  or: .venv/bin/python harness/tc.py check go__go-humanize__comma__Comma"
echo "                  or: .venv/bin/python harness/tc.py check javascript__qs__lib_stringify__stringify"
echo "                  or: .venv/bin/python harness/tc.py check rust__strsim-rs__src_lib__osa_distance"
echo "                  or: .venv/bin/python harness/tc.py check java__commons-codec__src_main_java_org_apache_commons_codec_language_Soundex__soundex"
echo "                  or: .venv/bin/python harness/tc.py check cpp__pugixml__src_pugixml__sort"
