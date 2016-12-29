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
    libgtk-3-dev gir1.2-webkit-3.0

# Adding the application and requirements to the image
ADD /src /src

# Get pip to download and install requirements:
RUN pip install -r /src/requirements.desktop_app.txt

# Creation of
RUN mkdir /src/djangotrellostats/media

# Creation of sqlite database
RUN echo > /src/djangotrellostats/db/djangotrellostats.db

# Expose ports
EXPOSE 8000
EXPOSE 9090

# Set the default directory where CMD will execute
WORKDIR /src

# Change to python manage.py runserver to run web app
CMD python desktop_app_main.py