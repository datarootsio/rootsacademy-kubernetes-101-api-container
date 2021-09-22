FROM python:3.8

# Copy function code
COPY ["main.py", "wsgi.py", "requirements.txt", "entrypoint.sh", "./"]

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
