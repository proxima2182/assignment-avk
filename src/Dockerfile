FROM python:3.9

# set a directory for the app
WORKDIR /src

# copy all the files to the container
COPY . .

# set environment
ENV FLASK_APP __init__.py
ENV FLASK_ENV development
ENV FLASK_RUN_PORT 7000
ENV FLASK_RUN_HOST 0.0.0.0
EXPOSE 7000

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["flask", "run", "--no-reload"]