FROM nginx

RUN mkdir -p /var/www/cache/tmp
RUN rm /etc/nginx/conf.d/*
RUN rm /var/log/nginx/*
COPY ./ssl/certs/dangercrossing.crt /etc/ssl/certs
COPY ./ssl/private/dangercrossing.key /etc/ssl/private