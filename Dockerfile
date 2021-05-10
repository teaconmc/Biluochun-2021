# Dependencies stage
# Use full image to build things
FROM python:3.9 AS dependencies
COPY requirements.txt /app/
WORKDIR /app/
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && pip3 install -r requirements.txt

# Build stage
FROM python:3.9-slim AS build
COPY --from=dependencies /app/ /app/
COPY ./ /app/

# Run stage
# Use slim to cut down image size
FROM python:3.9-slim
WORKDIR /app
RUN mkdir -p /app/data
VOLUME /app/data
COPY --from=build /app/ /app/
# Copy default config file
COPY --from=build /app/config.py /app/data/
ENV BILUOCHUN_CONFIG_PATH="/app/data/config.py"
ENTRYPOINT . venv/bin/activate \
           && gunicorn -w 1 -b 0.0.0.0:8080 -k gevent 'biluochun:create_app()'
EXPOSE 8080/tcp
