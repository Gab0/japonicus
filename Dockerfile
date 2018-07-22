FROM python:3.6.6-jessie


ENV LANG en_US.UTF-8

# install dependencies;
#RUN apt-get update -y
#RUN apt-get install software-properties-common python-software-properties -y


RUN apt-get update -y
RUN apt-get upgrade -y


RUN apt-get install python3-pip python3-numpy -y

RUN pip3.6 install --upgrade pip

COPY ./requirements.txt /opt/japonicus/requirements.txt

# those are required to build other python modules, so install first;
RUN pip3.6 install numpy cython pandas

RUN pip3.6 install --ignore-installed -r /opt/japonicus/requirements.txt


WORKDIR /opt/japonicus/

COPY . /opt/japonicus

EXPOSE 5000

RUN python3.6 --version

ENTRYPOINT ["python3.6", "/opt/japonicus/japonicus.py"]
CMD ["python3.6", "/opt/japonicus/japonicus.py", "--help"]
