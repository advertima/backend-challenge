FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY *.py /app

VOLUME ["/data"]
ENV SQLALCHEMY_DATABASE_URL=sqlite:////data/timeline_app.db
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
