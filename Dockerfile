ARG TENSORFLOW_VERSION=1.12.0-py3
FROM tensorflow/tensorflow:${TENSORFLOW_VERSION}

SHELL ["/bin/bash", "-c"]

RUN add-apt-repository ppa:jonathonf/python-3.6 --yes

RUN apt-get update -qq && \
  apt-get install -y --no-install-recommends \
  build-essential \
  bzip2 \
  colordiff \
  curl \
  git-core \
  graphviz \
  graphviz-dev \
  libffi-dev \
  libffi6 \
  libssl-dev \
  nano \
  openssh-client \
  openssl \
  pkg-config \
  python-tk \
  tk \
  unzip \
  vim \
  wget \
  xz-utils \
  hdf5-tools \
  cmake \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
  mkdir /app &&\
  mkdir -p /root/.ssh && chmod 0700 /root/.ssh && \
  ssh-keyscan github.com >/root/.ssh/known_hosts

WORKDIR /app

# add Python dependencies:
COPY requirements.txt /app
COPY . /app
RUN pip install -r requirements.txt

VOLUME ["/.history"]

ENV HISTFILE="/.history/bash_history"
ENV PYTHONPATH="/app"

# autocompletion for make and useful defaults:
RUN echo 'complete -W "\$(grep -oE '"'"'^[a-zA-Z0-9_-]+:([^=]|$)'"'"' Makefile | sed '"'"'s/[^a-zA-Z0-9_-]*$//'"'"'\)" make' >> /root/.bashrc && \
  echo 'export PS1="\w\$ "' >> /root/.bashrc && \
  cp /root/.bashrc /.bashrc && \
  ln -f -s python3.5 /usr/bin/python

CMD ["bash"]
