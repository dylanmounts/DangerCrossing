FROM nginx

RUN mkdir -p /var/www/cache/tmp
RUN rm /etc/nginx/conf.d/*
RUN rm /var/log/nginx/*

COPY ./ssl/certs /etc/ssl/certs
COPY ./ssl/private /etc/ssl/private

RUN if [ "$SELF_SIGNED_CERT" = "1" ]; then \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/dangercrossing.key -out /etc/ssl/certs/dangercrossing.crt -subj "/C=US/ST=SomeState/L=SomeCity/O=CompanyName/OU=Org/CN=dangercrossing.com"; \
fi