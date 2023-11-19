FROM python:3.9

# set a directory for the app
WORKDIR /app

# copy all the files to the container
COPY . .

# set environment
ENV FLASK_APP __init__.py
# ENV FLASK_ENV development
ENV FLASK_RUN_PORT 7000
ENV FLASK_RUN_HOST 0.0.0.0
EXPOSE 7000

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# create package info to make test script know root directory
RUN pip install -e .

CMD ["flask", "run"]