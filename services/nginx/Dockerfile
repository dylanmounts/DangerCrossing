FROM nginx

ARG SELF_SIGNED_SSL_CERT

RUN mkdir -p /var/www/cache/tmp
RUN rm /etc/nginx/conf.d/*
RUN rm /var/log/nginx/*

COPY ./ssl/certs /etc/ssl/certs
COPY ./ssl/private /etc/ssl/private

RUN if [ $SELF_SIGNED_SSL_CERT = 1 ]; then \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/DangerCrossing.key -out /etc/ssl/certs/DangerCrossing.crt -subj "/C=US/ST=MO/CN=DangerCrossing.com"; \
fi