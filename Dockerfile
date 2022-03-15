FROM --platform=linux/amd64 python:3.8

# Copy function code
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
