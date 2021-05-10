# Build stage
# Use full image to build things
FROM python:3.9 AS build
COPY ./ /app/
WORKDIR /app/
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && pip3 install -r requirements.txt

# Run stage
# Use slim to cut down image size
FROM python:3.9-slim
WORKDIR /app
RUN mkdir -p /app/data
VOLUME /app/data
COPY --from=build /app/ /app/
COPY --from=build /app/config.py /app/data/
ENV BILUOCHUN_CONFIG_PATH="/app/data/config.py"
# Bind to 0.0.0.0 instead of 127.0.0.1 so that we don't need to configure proxy
ENTRYPOINT . venv/bin/activate \
           && gunicorn -w 1 -b 0.0.0.0:8080 -k gevent 'biluochun:create_app()'
EXPOSE 8080/tcp
