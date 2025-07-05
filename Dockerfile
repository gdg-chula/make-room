FROM python:3.12-slim

# copy files to container
COPY . .

# install python dependencies
RUN pip install -r requirements.txt

# run main bot script
CMD ["python3", "main.py"]