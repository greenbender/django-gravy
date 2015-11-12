Gravy
=====

Gravy is a set of useful extensions to Django that I found myself reusing.


Requirements
------------

To enable all features of gravy you will need to install the following python packages:

  - django-betterforms => gravy.forms
  - django-widget-tweaks => gravy/templates/gravy/form_snippet.html
  - django-redis => gravy.websocket
  - gevent-websocket => gravy.websocket
  - jsonschema => gravy.forms
  - beautifulsoup4 => gravy.templatetags.gravytags ({% staticonce %} and {% prettyhtml %})
  - python-magic => gravy.utils
  - pillow => gravy.images
  - pytesseract => gravy.images
  - geoip2 => gravy.geo.geoip2


Additional dependencies (aptitude):

  - python-pip
  - redis-server => django-redis
  - libgeoip1 => django (for django.contrib.gis.geoip used by gravy.geo.geoip)
  - libjpeg-dev => pillow
  - libpng12-dev => pillow
  - tesseract-ocr => pytesseract
  - liblzo2-2 => gravy.lzo
  - libmaxminddb0 => geoip2
  - libmaxminddb-dev => geoip2
  - mmdb-bin => geoip2


If you are using geoip or geoip2 then you will also databases from maxmind.


Installation
------------

A complete install goes something like this. You're install might be a bit different (virtualenv etc)

    sudo apt-get install python-pip redis-server libgeoip1 libjpeg-dev libpng12-dev tesseract-ocr liblzo2-2 libmaxminddb0 libmaxminddb-dev mmdb-bin
    sudo pip install django-widget-tweaks django-redis gevent-websocket jsonschema beautifulsoup4 pillow pytesseract geoip2
    sudo pip install django-gravy


Features
--------

Many ... Until I get time to update this check the source code.
