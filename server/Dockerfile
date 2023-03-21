# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

ENV PYTHONUNBUFFERED=1

WORKDIR /server

RUN apk add --no-cache \
        --virtual=.build-dependencies \
        ninja g++ gfortran file binutils \
        musl-dev python3-dev openblas-dev lapack-dev && \
    apk add libstdc++ openblas lapack 

COPY requirements.txt /server
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /server

EXPOSE 8080

ENTRYPOINT ["python3"]
CMD ["routes.py"]

FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF
# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /