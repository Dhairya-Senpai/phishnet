FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    postfix \
    python3 \
    python3-urllib3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY main.cf /etc/postfix/main.cf
COPY master.cf /etc/postfix/master.cf
COPY pipe_to_api.py /usr/local/bin/pipe_to_api.py
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /usr/local/bin/pipe_to_api.py /entrypoint.sh

EXPOSE 2525

CMD ["/entrypoint.sh"]
