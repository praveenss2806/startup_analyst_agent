FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code
  
# If running behind a proxy like Nginx or Traefik add --proxy-headers
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8080"]