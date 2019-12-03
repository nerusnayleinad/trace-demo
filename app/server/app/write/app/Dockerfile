FROM debian

RUN apt-get update && apt-get install -y python3 python3-pip
RUN mkdir /code
ADD ./service.py /code
ADD ./requirements.txt /code/
RUN pip3 install -r /code/requirements.txt
ENV SERVICE_NAME write
CMD ["python3", "/code/service.py", "--project_id", "ackstorm-demo-project"]