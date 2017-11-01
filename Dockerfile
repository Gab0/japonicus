FROM gekko:latest
# builds on top of Gekko's docker image, so build it, named gekko ;

ENV LANG en_US.UTF-8

# install dependencies;
RUN apt-get update -y
RUN apt-get install git python3-pip python3 pandoc -y

RUN pip3 install --upgrade
RUN pip3 install pypandoc

COPY . /opt/japonicus
RUN pip3 install -r /opt/japonicus/requirements.txt


ENTRYPOINT "/bin/bash"