FROM gekko:latest
# builds on top of Gekko's docker image, so build it, named gekko ;
# install dependencies;
RUN apt-get update -y
RUN apt-get install git python3-pip python3 -y

RUN pip install --upgrade
RUN pip install deap



RUN git clone https://github.com/askmike/gekko.git

COPY . /opt/japonicus

ENTRYPOINT "/bin/bash"