FROM httpd:2.4

RUN apt-get update \
    && \
    apt-get -y install \
       curl jq \
    && \
    apt-get clean

RUN echo '# Added by docker build' >> /usr/local/apache2/conf/httpd.conf
RUN echo 'Include conf/local-conf.d/*.conf' >> /usr/local/apache2/conf/httpd.conf
