FROM python:3-buster

RUN apt-get clean && apt-get -y update
RUN apt-get -y install nginx \
    && apt-get -y install python3-dev 
COPY requirements.txt /www/api/requirements.txt
WORKDIR /www/api

RUN pip3 install -r requirements.txt --src /usr/local/src

COPY ./* /www/api/
COPY ./DataModel/* /www/api/DataModel/
COPY ./certs/* /certs/
COPY nginx.conf /etc/nginx
RUN chmod +x ./start.sh

CMD ["./start.sh"]

     
    
