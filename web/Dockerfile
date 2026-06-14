FROM nginx:1.27-alpine
# A imagem oficial do nginx processa /etc/nginx/templates/*.template com envsubst
# na inicialização, gerando /etc/nginx/conf.d/default.conf com as variáveis de
# ambiente substituídas (aqui, GATEWAY_UPSTREAM).
ENV GATEWAY_UPSTREAM=gateway:8000
COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY public /usr/share/nginx/html
EXPOSE 80
