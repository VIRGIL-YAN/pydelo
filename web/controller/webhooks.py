# -*- coding:utf-8 -*-
import time
from web.utils.log import Logger
logger = Logger("web.controllers.webhooks")

from web import app
from web.services.users import users
from web.services.hosts import hosts
from web.services.deploys import deploys
from web.services.projects import projects
from .login import authorize

from flask import request, jsonify, g

# 添加git的webhook像这样：http://10.169.123.172:9998/api/webhooks/push_events?apikey=FWi14sULr0CwdYqhyBwQfbpdSEV7M8dp&project_id=9&host_id=1
@app.route('/api/webhooks/push_events', methods=["POST"])
@authorize
def webhooks_push_events():
    project_id = request.args.get("project_id")
    host_id = request.args.get("host_id")
    data = request.json
    branch = data["ref"].split("/", 2)[-1]
    version = data["after"][:7]
    logger.debug(repr(data))
    # 只针对dev分支进行deploy
    if data["ref"] == "refs/heads/dev" and data["total_commits_count"] > 0:
        deploy = deploys.create(
            user_id=g.user.id,
            project_id=project_id,
            host_id=host_id,
            mode=0,
            status=3,
            branch=branch,
            version=version,
            softln_filename=time.strftime("%Y%m%d-%H%M%S") + "-" + version,
            )
        deploys.deploy(deploy)
        return jsonify({"rc": 0}), 200
    else:
        return jsonify({"rc": 0}), 204

@app.route('/api/webhooks/tag_push_events', methods=["POST"])
@authorize
def webhooks_tag_push_events():
    project_id = request.args.get("project_id")
    host_id = request.args.get("host_id")
    data = request.json
    tag = data["ref"].split("/", 2)[-1]
    logger.debug(repr(data))
    # 只针对tag push
    if data["object_kind"] == "tag_push" and data["total_commits_count"] > 0:
        deploy = deploys.create(
            user_id=g.user.id,
            project_id=project_id,
            host_id=host_id,
            mode=1,
            status=3,
            branch="",
            version=tag,
            softln_filename=time.strftime("%Y%m%d-%H%M%S") + "-" + tag,
            )
        deploys.deploy(deploy)
        return jsonify({"rc": 0}), 200
    else:
        return jsonify({"rc": 0}), 204
