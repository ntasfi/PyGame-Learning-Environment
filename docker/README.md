# Run PyGame-Learning-Environment on Docker

## Setup
`wget http://raw.githubusercontent.com/ntasfi/PyGame-Learning-Environment/master/docker/Dockerfile`

## Build PLE image
`docker build -t ple .`

#### UBUNTU:  
`docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=unix$DISPLAY ple /bin/bash`

#### MAC:
in a separate window run:  
  `brew install socat`  
  `socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\"`

finally, run `ifconfig` and look for the ip of vboxnet0, say `192.168.99.1`  

  `docker run -i -t -e DISPLAY=192.168.99.1:0 ple /bin/bash`

## Usage:
  `cd ple/examples`  
  `python keras_nonvis.py`
