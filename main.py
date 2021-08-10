import os
import json
from flask import Flask, jsonify
import redis
from processors import http_processor
import datetime
from flask import current_app

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('configs/config.py', silent=True)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/status')
    def get_all_status():
        r = redis.StrictRedis(host="localhost")
        list = []
        for conf in app.config["HEALTHCONFIGS"]:
            list.append(conf["name"])
        health_list = []
        for i in list:
            data = r.get("health_"+i)
            health_list.append({i: data.decode("utf-8"), "last_update": r.get("last_updated_"+i).decode("utf-8")})
        print(health_list)
        return jsonify(health_list)

    @app.route('/status/<service_name>')
    def get_single_app_status(service_name):
        r = redis.StrictRedis(host="localhost")
        data = r.get("health_" + service_name)
        return jsonify({service_name: data.decode("utf-8"), "last_update": r.get("last_updated_"+service_name).decode("utf-8")})

    @app.cli.command()
    def update_status():
        r = redis.StrictRedis(host="localhost")
        """Run scheduled job."""
        print('Updating Health Status...')
        config = current_app.config
        list = config["HEALTHCONFIGS"]
        for i in list:
            print("Updating app: "+ i["name"])
            now = datetime.datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            if i["type"]=="HTTP":
                value=http_processor.processor(url = i["url"], method=i["method"], status_code=i["success_codes"])
                if value:
                    r.set("health_"+i["name"], "ok")
                else:
                    r.set("health_"+i["name"], "failed")
                r.set("last_updated_" + i["name"], dt_string)
        print('Done!')
    return app