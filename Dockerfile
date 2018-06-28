FROM gekko
# builds on top of Gekko's docker image, so build it, named gekko ;

ENV LANG en_US.UTF-8

# install dependencies;
RUN apt-get update -y
RUN apt-get install pandoc python3 python3-pip -y

RUN pip3 install --upgrade

COPY ./requirements.txt /opt/japonicus/requirements.txt
RUN pip3 install -rI /opt/japonicus/requirements.txt

WORKDIR /opt/japonicus/

COPY . /opt/japonicus

EXPOSE 5000

RUN python3 --version

CMD ["python3", "/opt/japonicus/japonicus.py"]
