FROM python:3.9

WORKDIR /tests

COPY requirements.txt /tests/
RUN pip install -r requirements.txt

COPY *.py /tests

CMD ["python", "-m", "unittest"]
