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
    swig cmake fontconfig libfontconfig1-dev \
    libjpeg-dev libtiff-dev libopenjpeg-dev \
    libapache2-mod-wsgi apache2 wget unzip

WORKDIR /code

# Poppler
RUN git clone git://git.freedesktop.org/git/poppler/poppler 

WORKDIR /code/poppler

# Patch poppler > 0.19
RUN git checkout -b multivio poppler-0.42.0 \
    && perl -pi.bak -e 's/globalParams->getOverprintPreview\(\)/gTrue/g' poppler/SplashOutputDev.h

#poppler 0.18
#RUN git checkout poppler-0.18

RUN mkdir -p /code/poppler/build && cd /code/poppler/build \
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
	&& pip install --global-option=build_ext .

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

WORKDIR /var/www/multivio/client
RUN wget http://demo.multivio.org/multivio/client_1.0.0.zip \
    && unzip client_1.0.0.zip \
    && mv client_1.0.0/* . \
    && rm -fr client_1.0.0 client_1.0.0.zip \
    && chown -R www-data:www-data /var/www/multivio/client

#WORKDIR /
# Slim down image
#RUN rm -fr /code \
#RUN apt-get clean autoclean \
#    && rm -rf /var/lib/{apt,dpkg}/ \
#    && find /usr/share/doc -depth -type f ! -name copyright -delete \
#    && find /usr/share/doc -empty -delete \
#    && rm -rf /usr/share/man/* /usr/share/groff/* /usr/share/info/* \
#    && rm -rf /tmp/* /var/lib/{cache,log}/ /root/.cache/* \
#    && apt-get -qy remove --purge g++ make git python-dev python-pip swig wget unzip \
#    && apt-get -qy autoremove

#USER multivio
#VOLUME ["/code"]
CMD ["httpd-foreground"]

#CMD ["rerodoc", "--debug", "run", "-h", "0.0.A0.0"]
