# DOCKER-VERSION 1.11.1
#
# docker build --tag alleninstitute/allensdk .
# docker run -it alleninstitute/allensdk /bin/bash
#
FROM continuumio/miniconda3:4.5.11

MAINTAINER Tim Fliss <timf@alleninstitute.org>

RUN apt-get update; \
    apt-get install -y linux-headers-amd64 build-essential; \
    apt-get install -y vim procps postgresql-client libgl1-mesa-glx; \
    pip install --upgrade pip; \
    mkdir -p /var/www/static; \
    rm -rf /var/lib/apt/lists/*

COPY ./create_conda_envs.sh .
RUN chmod +x create_conda_envs.sh

ARG BLUE_SKY_USERID=1066
ARG BLUE_SKY_USERNAME=blue_sky_user

RUN \
 useradd -u ${BLUE_SKY_USERID} ${BLUE_SKY_USERNAME}; \
 chsh -s /bin/bash ${BLUE_SKY_USERNAME}; \
 mkdir /home/${BLUE_SKY_USERNAME}; \
 mkdir -p /blue_green/logs; \
 mkdir /blue; \
 mkdir /green; \
 chown -R ${BLUE_SKY_USERNAME} /blue_green; \
 chown ${BLUE_SKY_USERNAME} /blue; \
 chown ${BLUE_SKY_USERNAME} /green; \
 chown ${BLUE_SKY_USERNAME} /home/${BLUE_SKY_USERNAME}; \
 chmod -R go+rw /home/${BLUE_SKY_USERNAME}

COPY ./jupyter_notebook_config.json ./jupyter_notebook_config.py /home/blue_sky_user/.jupyter/
