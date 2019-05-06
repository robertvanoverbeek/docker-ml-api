FROM tiangolo/uwsgi-nginx-flask:python3.6

# read more info on https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/
# such as:

# By default, the container made from this image will listen on port 80.
# To change this behavior, set the LISTEN_PORT environment variable. You might also need to create the respective EXPOSE Docker instruction.
# You can do that in your Dockerfile, it would look something like:
# FROM tiangolo/uwsgi-nginx-flask:python3.7
# ENV LISTEN_PORT 8080
# EXPOSE 8080



WORKDIR /app/

COPY requirements.txt /app/
RUN pip install -r ./requirements.txt

ENV LISTEN_PORT 8080

EXPOSE 8080

COPY main.py __init__.py /app/
