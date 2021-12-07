FROM httpd:2.4
COPY ./assets/ /usr/local/apache2/htdocs/
RUN find /usr/local/apache2/htdocs -type d -exec chmod u+rwx,g+rx,o+rx {} +
RUN find /usr/local/apache2/htdocs -type f -exec chmod u+rw,g+r,o+r {} +