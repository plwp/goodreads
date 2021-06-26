FROM python:3-buster
# Run requirements installation first to keep the container delta small on code changes
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
COPY ./ /app/

# Run the service on start
ENTRYPOINT ["python3", "/app/averager.py"]
