# Era toolchain for Java repos (2017-2019): Maven 3.6 + OpenJDK 8.
# maven:3.6-jdk-8-slim (the guide's choice) has no linux/arm64 variant; this host is arm64, and
# emulating amd64 would distort runtime/energy measurements. maven:3.6-amazoncorretto-8 is the
# same Maven 3.6 line on Amazon Corretto 8 (an OpenJDK 8 build) and runs natively.
# ~/.m2 is mounted from the shared named volume tc-cache-m2 (see benchmark/repos/java__*.json).
# Base image pinned by digest (checked on 2026-10-20 to be the exact base of the images used for all published results).
FROM maven:3.6-amazoncorretto-8@sha256:c7bca04b47d1b84a04d9bee14ab6d7fc9be3b7f847079f39a7cb86a62e011f56
ENV MAVEN_OPTS="-Xmx1g"
ENTRYPOINT []
WORKDIR /w
