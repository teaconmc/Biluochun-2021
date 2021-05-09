# Build stage
FROM python:3.9 AS build
COPY ./ /app/
WORKDIR /app/
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && pip3 install -r requirements.txt

# Run stage
FROM python:3.9
WORKDIR /app
RUN mkdir -p /app/private
VOLUME /app/private
COPY --from=build /app/ /app/
COPY --from=build /app/config.py /app/private/
ENV BILUOCHUN_CONFIG_PATH="/app/private/config.py"
ENTRYPOINT . venv/bin/activate \
           && gunicorn -w 1 -b 127.0.0.1:8080 -k gevent 'biluochun:create_app()'
EXPOSE 8080/tcp
