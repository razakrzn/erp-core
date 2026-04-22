FROM Python 3.12

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3001

CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:3001"]