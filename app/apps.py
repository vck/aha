#!/usr/bin/env python
# coding=utf-8

from os import getenv
import random
import string
import redis

from flask import (
    Flask,
    redirect,
    request,
    url_for,
    jsonify
)

# redis instance
r = redis.Redis(host="localhost")

# flask instance and config
# use debug mode
# set port 8000
app = Flask(__name__)
app.debug = True
app.config["PORT"] = int(getenv("PORT", 8000))


def generate_id():
    """
    generate random string with randomly picked
    string
    """

    return ''.join(random.choice(string.ascii_uppercase
        + string.digits + string.lowercase) for _ in range(5))


def shorten(url, costum_key=None):
    """
    shorten url and return its random key.
    if costum_key is set,
    store costum key instead

    :params:
    @url: string
    @costum_key: string
    @costum_key: default: None

    :example:
    @no costum url
    shorten("http://goo.gl")

    @using costum url
    shorten("http://goo.gl", costum_key="goo")
    """

    # check if costum key is valid
    if costum_key:
        # check if wheter costum key has been generated or not
        if costum_key not in r.lrange("costum:urls", 0, 10000):
            # if costum key is available
            url_hash = '%s' % costum_key
            # store string with SET url:{costum_key}:id
            r.set('url:{}:id'.format(url_hash), url)
            # store costum key to list costum:urls with LPUSH
            r.lpush('costum:urls', url_hash)
            # return costum key
            return url_hash
        # if costum key has been generated, return None
        return None

    url_hash = '%s' % generate_id()
    r.set('url:{}:id'.format(url_hash), url)
    r.lpush('global:urls', url_hash)
    return url_hash


def expand(key):
    """
    get key from list with GET command
    """

    return r.get("url:{}:id".format(key))


@app.route("/")
def index_page():
    """
    main endpoint
    """

    return "aha  v0.1"


@app.route("/<key>")
def redirect_url(key):
    """
    redirect to related url with key

    :params: key : string
    """

    url = expand(key)
    if url:
        return redirect(url, 301)
    return jsonify({"msg": "key not found!"})


@app.route("/api/add", methods=["GET", "POST"])
def shorten_me():
    """
    endpoint for generating random urls

    :params:
    @url: string

    :methods:
    @GET
    @POST

    :example:
    @url: localhost

    /api/costum?url=localhost

    :return:

    {
    "data": {
        "key": "P8LnW",
        "url": "http://localhost/P8LnW"
    },
    "status": "OK"
    }
    """

    if request.method in ["GET", "POST"]:
        url = request.args.get("url")
        ckey = request.args.get('key')

        if url:
            key = shorten(url)
            payload = {"status": "OK",
                    "data": {"key": key,
                    "url": "http://localhost/{}".format(key)}}
            return jsonify(payload)
        return jsonify({"msg": "url not spesified"})
    return jsonify({"msg": "request invalid"})


@app.route("/api/costum", methods=["GET", "POST"])
def costum_shortener():
    """
    endpoint for generating costum urls

    :params:
    @url: string
    @key: string

    :methods:
    @GET
    @POST

    :example:
    @url: localhost
    @key: lcl
    /api/costum?url=localhost&key=lcl

    :return:
    {
    "data": {
        "key": "lcl",
        "url": "http://localhost/lcl"
    },
    "status": "OK"
    }
    """

    if request.method in ["GET", "POST"]:
        url = request.args.get("url")
        ckey = request.args.get('key')

        if url and ckey:
            key = shorten(url, costum_key=ckey)
            if key:
                payload = {"status": "OK",
                    "data": {"key": key,
                    "url": "http://localhost/{}".format(key)}}
                return jsonify(payload)
            return jsonify({"msg": "key has been taken"})
        return jsonify({"msg": "url or costum key not spesified"})
    return jsonify({"msg": "request invalid"})


@app.route("/api/info", methods=["GET", "POST"])
def get_all_urls():
    """
    :rtype: JSON
    endpoint for retreiving information about shortened url(s)
    """

    random_keys = r.lrange("global:urls", 0, 10000)
    costum_keys = r.lrange("costum:urls", 0, 10000)
    return jsonify({
    "status": "OK", "data": {
    "random_key": random_keys,
    "costum_key": costum_keys},
    "random_urls_count": len(random_keys),
    "costum_urls_count": len(costum_keys)})
