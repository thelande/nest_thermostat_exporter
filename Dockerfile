FROM python:3.8-alpine as builder

RUN set -eux; \
    apk add --no-cache \
        git \
    ; \
    pip install --no-cache-dir --progress-bar off \
        pbr

WORKDIR /usr/src/app
COPY . .

RUN set -eux; \
    python setup.py bdist_wheel

FROM python:3.8-alpine as application
LABEL maintainer="Thomas Helander <thomas.helander@gmail.com>"

COPY --from=builder /usr/src/app/dist/*.whl /
RUN set -eux; \
    pip install --no-cache-dir --progress-bar off /*.whl

ENTRYPOINT ["nest_thermostat_exporter"]
