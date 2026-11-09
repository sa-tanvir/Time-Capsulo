# Base image pinned by digest (checked on 2026-10-21 to be the exact base layer of tc-cpp). The apt packages (g++-9 9.4.0, cmake 3.16.3, make 4.2.1) come from the Ubuntu 20.04 archive at build time.
# Era toolchain for C++ repos (2017-2019): GCC 9 + CMake 3.16 + make (Ubuntu 20.04 ships exactly these;
# much smaller than the official gcc:9 image).
FROM ubuntu:20.04@sha256:8feb4d8ca5354def3d8fce243717141ce31e2c428701f6682bd2fafe15388214
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends g++-9 gcc-9 cmake make python3 ca-certificates \
 && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-9 90 \
 && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 90 \
 && update-alternatives --install /usr/bin/c++ c++ /usr/bin/g++-9 90 \
 && update-alternatives --install /usr/bin/cc cc /usr/bin/gcc-9 90 \
 && rm -rf /var/lib/apt/lists/*
# The harness restores pristine sources with their original (old) mtimes, which would make
# make/ninja skip recompilation. tc-sync-mtimes touches every file whose content changed since
# the previous call (content-hash manifest kept in the build volume) so incremental builds stay correct.
COPY cpp-sync-mtimes.sh /usr/local/bin/tc-sync-mtimes
COPY cpp-doctest2junit.py /usr/local/bin/tc-doctest2junit
RUN chmod +x /usr/local/bin/tc-sync-mtimes /usr/local/bin/tc-doctest2junit
WORKDIR /w
