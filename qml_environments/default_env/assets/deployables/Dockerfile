# 
FROM python:3.8.13

# 
WORKDIR /code

# 
COPY ./server_requirements.txt /code/server_requirements.txt
COPY ./proj_requirements.txt /code/proj_requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/proj_requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/server_requirements.txt

# 
COPY ./app /code/app

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]