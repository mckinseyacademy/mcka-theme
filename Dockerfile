FROM ubuntu:xenial

WORKDIR ./edx/app/apros/mcka_apros

RUN apt-get update -qq; true
RUN apt-get -y upgrade
RUN apt-get install -qqy sudo nano git
RUN apt-get install -qqy python3.5 python3.5-dev python3-pip virtualenv build-essential libssl-dev

RUN apt-get update --fix-missing && apt-get install locales
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

COPY ./docs/provision_script_docker.sh ./docs/provision_script_docker.sh
COPY ./requirements.txt ./requirements.txt

RUN chmod +x ./docs/provision_script_docker.sh
RUN ./docs/provision_script_docker.sh
