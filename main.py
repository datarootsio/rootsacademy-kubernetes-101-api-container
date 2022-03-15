# app.py - a minimal flask api using flask_restful
import pprint
import os

from flask import Flask, jsonify
from flask_restx import Resource, Api
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import BadRequest
from google.cloud import bigquery

app = Flask(__name__)

VERSION = os.getenv("VERSION", "0.0.1")
PROJECT_ID = os.getenv("PROJECT_ID", "rootsacademy")
MAX_TWEETS = int(os.getenv("MAX_TWEETS", 10))
STUDENT = os.getenv("STUDENT", "reference")

api = Api(
    app,
    version=VERSION,
    title=f"Tweet reader ({STUDENT})",
    description=f"Rootsacademy Tweet Reader ({STUDENT})",
)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
app.config["EXECUTOR_PROPAGATE_EXCEPTIONS"] = True
app.config["EXECUTOR_MAX_WORKERS"] = 15


@api.route("/hello")
@api.doc()
class HelloWorld(Resource):
    def get(self):
        return jsonify(student=STUDENT, hello="world")


@api.route("/alive")
@api.doc()
class Ping(Resource):
    def get(self):
        return jsonify(alive=True)


@api.route("/version")
@api.doc()
class Version(Resource):
    def get(self):
        return jsonify(version=VERSION)


@api.route("/api/debug")
@api.doc()
class Debug(Resource):
    def post(self):
        pprint.pprint(api.payload)  # pragma: no cover
        return jsonify(status="OK")


@api.route("/api/tweets/count")
@api.doc()
class TweetCount(Resource):
    def get(self):
        bigquery_client = bigquery.Client()
        dataset_ref = bigquery_client.get_dataset("ml_tweets")

        table_ref = dataset_ref.table("ml_tweets")
        table = bigquery_client.get_table(table_ref)  # API call

        myquery = f"select count(*) size from `{PROJECT_ID}.ml_tweets.ml_tweets`"
        job = bigquery_client.query(myquery)
        result = job.result()
        records = 0
        for row in result:
            records = row.size

        return jsonify(count=records)


@api.route("/api/tweets/last/", defaults={"count": MAX_TWEETS}, doc={})
@api.route(
    "/api/tweets/last/<count>",
    doc={"params": {"count": "Number of tweets to send back (1 to 50)"}},
)
class LastTweets(Resource):
    def get(self, count):
        bigquery_client = bigquery.Client()
        dataset_ref = bigquery_client.get_dataset("ml_tweets")

        table_ref = dataset_ref.table("ml_tweets")
        table = bigquery_client.get_table(table_ref)  # API call

        myquery = f"select * from `{PROJECT_ID}.ml_tweets.ml_tweets` ORDER BY created_at DESC LIMIT {max(1,min(int(count),50))}"

        job = bigquery_client.query(myquery)
        records = [dict(row) for row in job]

        return jsonify({"count": len(records), "tweets": records})


@api.route("/api/bad-request")
@api.doc()
class BadRequest(Resource):
    def get(self):
        raise BadRequest("THIS IS BAD")
