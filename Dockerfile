#
# Multivio docker build
#
FROM debian:jessie
MAINTAINER Johnny Mariéthoz <Johnny.Mariethoz@rero.ch>

# Node.js, bower, less, clean-css, uglify-js, requirejs
RUN apt-get update
RUN apt-get -qy upgrade --fix-missing --no-install-recommends

# Install dependencies
RUN apt-get -qy install --fix-missing --no-install-recommends \
    g++ make git python python-dev python-pip \
    swig cmake cmake-curses-gui fontconfig libfontconfig1-dev \
    libcairo2-dev libjpeg-dev libtiff-dev vim libopenjpeg-dev \
    libapache2-mod-wsgi apache2

WORKDIR /code

# Poppler
RUN git clone git://git.freedesktop.org/git/poppler/poppler \
	&& cd /code/poppler \
	&& git checkout -b multivio origin/poppler-0.18 \
	&& mkdir -p /code/poppler/build && cd /code/poppler/build \
	&& cmake -Wno-dev -D ENABLE_XPDF_HEADERS=True ../ \
    && make -j 2 install

# make libpoppler globally available
RUN ldconfig /usr/local/lib

# Multivio server
COPY . /code/multivio
WORKDIR /code/multivio

# Basic Python
RUN pip install --upgrade pip setuptools \
	#install multivio
	&& pip install -e .

# Multivio client

#RUN adduser --uid 1000 --disabled-password --gecos '' multivio
#RUN chown -R multivio:multivio /code

# apache
RUN mkdir -p /var/log/multivio /var/tmp/multivio /var/www/multivio/server \
    && cp tools/multivio_server.py /var/www/multivio/server \
    && cp tools/mvo_config_apache.py /var/www/multivio/server/mvo_config.py \
    && chown www-data:www-data /var/log/multivio /var/tmp/multivio /var/www/multivio \
    && cp tools/multivio.conf /etc/apache2/sites-available/ \
    && a2ensite multivio

# apache script
RUN cp scripts/httpd-foreground /usr/local/bin \
    && chmod a+x /usr/local/bin/httpd-foreground

#WORKDIR /
# Slim down image
#RUN rm -fr /code \
RUN apt-get clean autoclean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/{apt,dpkg}/ \
    && find /usr/share/doc -depth -type f ! -name copyright -delete \
    && find /usr/share/doc -empty -delete \
    && rm -rf /usr/share/man/* /usr/share/groff/* /usr/share/info/* \
    && rm -rf /tmp/* /var/lib/{cache,log}/ /root/.cache/*

#USER multivio
#VOLUME ["/code"]
CMD ["httpd-foreground"]

#CMD ["rerodoc", "--debug", "run", "-h", "0.0.A0.0"]
