# VERSION:        0.1
# DESCRIPTION:    PLE
# AUTHOR:         Eder Santana <edercsjr@gmail.com>
# COMMENTS:
#     Pygame learning environment
# SETUP:
#   # Download PLE Dockerfile
#   wget ...
#
#   # Build atom image
#   docker build -t ple .
#
#   UBUNTU:
#   docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix \
#       -e DISPLAY=unix$DISPLAY ple /bin/bash
#
#   MAC:
#   in a separate window run:
#       brew install socat
#       socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\"
#   finally:
#       run ifcongi and look for the ip of vboxnet0, say 192.168.99.1
#       docker run -i -t -e DISPLAY=192.168.99.1:0 ple /bin/bash
#
# USAGE:
#   cd ple/examples
#   python keras_nonvis.py

# FROM ubuntu:14.04
FROM ubuntu

MAINTAINER Eder Santana <edercsjr@gmail.com>

RUN apt-get update && apt-get install -y \
    mercurial \
    libav-tools \
    libsdl-image1.2-dev \
    libsdl-mixer1.2-dev \
    libsdl-ttf2.0-dev \
    libsmpeg-dev \
    libsdl1.2-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    libplib-dev \
    libopenal-dev \
    libalut-dev \
    libvorbis-dev \
    libxxf86vm-dev \
    libxmu-dev \
    libgl1-mesa-dev \
    python-dev \
    python-pip \
    python-numpy \
    python-scipy \
    python-pygame \
    git

# RUN hg clone https://bitbucket.org/pygame/pygame && cd pygame && python setup.py build && sudo python setup.py install && cd ..
RUN pip install keras git+https://github.com/ntasfi/PyGame-Learning-Environment.git
RUN git clone https://github.com/ntasfi/PyGame-Learning-Environment.git ple
