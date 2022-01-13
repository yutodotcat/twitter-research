# source: https://hub.docker.com/r/ototadana/fasttext/dockerfile/

FROM ototadana/nlp-jp

COPY ./dockerenv/requirements.txt /tmp/

RUN sudo apt-get update \
    && sudo apt-get install nkf unzip

RUN cd /tmp \
    && git clone https://github.com/facebookresearch/fastText.git \
    && cd fastText \
    && make \
    && cp /tmp/fastText/fasttext /usr/local/bin \
    && pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && rm -fr /tmp/fastText

ARG USERNAME=me
ARG GROUPNAME=me
ARG UID=1000
ARG GID=1000
ARG PASSWORD=user

RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID -G sudo $USERNAME && \
    echo $USERNAME:$PASSWORD | chpasswd && \
    echo "$USERNAME   ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER $USERNAME
