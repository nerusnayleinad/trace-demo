FROM debian

RUN apt-get update && apt-get install -y python3 python3-pip
RUN mkdir /code
ADD ./requirements.txt /code/
RUN pip3 install -r /code/requirements.txt
ADD ./service.py /code
ENTRYPOINT ["python3", "/code/service.py"]