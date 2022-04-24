From python:3.7.13

COPY . /Webproject

WORKDIR /Webproject

COPY requirements.txt ./
RUN pip install -r requirements.txt

#Uncomment just the next 2 lines to run your application in Docker container
EXPOSE 8080
CMD python server.py 8080

#Uncomment just the next line when you want to deploy your container on Heroku
#CMD python server.py $PORT

