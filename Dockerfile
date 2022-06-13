FROM python:3.9-slim-buster

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./src /src

WORKDIR /src
ENV PYTHONPATH /src

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"]
