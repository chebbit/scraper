FROM python:3.7-stretch

LABEL maintainer="dancetj@gmail.com"

RUN apt-get update && apt-get upgrade && apt-get install -y vim net-tools
COPY src /app
WORKDIR /app

RUN pip install -r /app/requirements.txt

# ENTRYPOINT ["python", "./app/my_script.py", "my_var"]
VOLUME /app/output

CMD ["bash"]
