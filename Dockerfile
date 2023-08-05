FROM python:3 
COPY . /master_planner
WORKDIR /master_planner/master_planner
COPY /master_planner/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 8000
ENTRYPOINT ["python3", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]