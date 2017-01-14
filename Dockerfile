# Dockerfile

# Set the base image to Ubuntu
FROM ubuntu:16.04

# File Author / Maintainer
MAINTAINER diegojromerolopez

# Update the sources list
RUN apt-get update

# Install Python2 and required dependencies
RUN apt-get install -y python2.7 python2.7-dev python-pip\
    libffi-dev libmysqlclient-dev libssl-dev libxml2-dev\
    libxslt1-dev python-gi python-gi-dev python-gobject\
    libgtk-3-dev gir1.2-webkit-3.0 python-virtualenv

# Adding the application and requirements to the image
ADD / /
RUN mkdir /src/djangotrellostats/media
WORKDIR /

# Expose ports
EXPOSE 8000
EXPOSE 9090

CMD run_desktop_app.sh
