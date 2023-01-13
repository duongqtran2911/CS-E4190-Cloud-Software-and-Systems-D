FROM ubuntu:18.04
WORKDIR /application
ARG PYTHON_VERSION=3.8
RUN apt-get -y update && \
    apt-get install build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev uuid-dev -y && \
    apt install wget -y && \
    if [ "$PYTHON_VERSION" = "3.9" ] ; then wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz; tar -xzvf Python-3.9.0.tgz; cd Python-3.9.0; ./configure; make; make install; cd ..; rm Python-3.9.0.tgz; rm -rf Python-3.9.0; fi && \
    if [ "$PYTHON_VERSION" = "3.8" ] ; then wget https://www.python.org/ftp/python/3.8.15/Python-3.8.15.tgz; tar -xzvf Python-3.8.15.tgz; cd Python-3.8.15; ./configure; make; make install; cd ..; rm Python-3.8.15.tgz; rm -rf Python-3.8.15; fi && \
    apt-get install python3-pip python-dev -y && \
    pip3 install --upgrade pip && \
    pip3 install pyLint pytest nbmake wheel && \
    if [ "$PYTHON_VERSION" = "3.8" ] ; then rm -f /usr/bin/python3; ln -s /usr/bin/python3.8 /usr/bin/python3; fi