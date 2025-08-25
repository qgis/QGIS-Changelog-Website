#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
# Note this base image is based on debian
FROM python:3.12-slim as prod
MAINTAINER Tim Sutton<tim@kartoza.com>

RUN  export DEBIAN_FRONTEND=noninteractive
ENV  DEBIAN_FRONTEND noninteractive
RUN  dpkg-divert --local --rename --add /sbin/initctl

# Pandoc needed to generate rst dumps, uic compressor needed for django-pipeline
RUN apt-get update -y && \
    apt-get -y install python3-gdal python3-geoip sudo curl rpl wget && \
    apt-get -y --force-yes install yui-compressor gettext && \
    apt-get -y --purge autoremove make libc-dev musl-dev g++ && \
    apt-get install -y nodejs npm && \
    npm install -g yuglify && \
    apt-get remove -y npm && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /root/.npm /root/.cache && \
    rm -rf ~/.cache/pip
RUN wget https://github.com/jgm/pandoc/releases/download/3.2/pandoc-3.2-1-amd64.deb
RUN dpkg -i pandoc-3.2-1-amd64.deb && rm pandoc-3.2-1-amd64.deb

# Added because of issue with building cryptography.io using pip
# This flag disabled rust build, but only for this particular version
# In the future, we may have to include rust toolchain in the Dockerfile
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN apt-get update -y && apt-get -y install git build-essential libpangocairo-1.0-0
ADD deployment/docker/REQUIREMENTS.txt /REQUIREMENTS.txt
ADD deployment/docker/uwsgi.conf /uwsgi.conf
ADD django_project /home/web/django_project
RUN pip install --upgrade pip && pip install -r /REQUIREMENTS.txt
RUN pip install uwsgi


# Open port 8080 as we will be running our uwsgi socket on that
EXPOSE 8080

#USER www-data

# Install NodeJS and webpack
RUN apt-get -qq update && apt-get -qq install -y --no-install-recommends wget && \
    wget --no-check-certificate https://deb.nodesource.com/setup_22.x -O /tmp/node.sh && bash /tmp/node.sh && \
    apt-get -qq update && apt-get -qq install -y nodejs build-essential

WORKDIR /home/web/django_project
COPY django_project/package.json /home/web/django_project/package.json
RUN npm install -g npm@11.1.0 && npm install -g webpack@5.98.0 && npm install -g webpack-cli@6.0.1 && npm install

WORKDIR /home/web/django_project
CMD ["uwsgi", "--ini", "/uwsgi.conf"]

FROM prod as dev

# This section taken on 2 July 2015 from
# https://docs.docker.com/examples/running_ssh_service/
# Sudo is needed by pycharm when it tries to pip install packages
RUN apt-get update && apt-get install -y openssh-server sudo
RUN mkdir -p /var/run/sshd
RUN echo 'root:docker' | chpasswd
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config


# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

# End of cut & paste section

ADD deployment/docker/REQUIREMENTS-dev.txt /REQUIREMENTS-dev.txt
RUN pip install --upgrade pip && pip install -r /REQUIREMENTS-dev.txt
ADD deployment/docker/bashrc /root/.bashrc

# --------------------------------------------------------
# Open ports as needed
# --------------------------------------------------------

# Open port 8000 as we will be running our django dev server on
EXPOSE 8000
# Open port 22 as we will be using a remote interpreter from pycharm
EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
