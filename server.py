import os
import flask
import json

from pathlib import Path
from werkzeug.wsgi import FileWrapper
from tempfile import NamedTemporaryFile

from typing import Dict, Any

from lfs.repository import Repository
from lfs.config import config_instance

config_instance.SetRoot(os.path.join(
    os.getcwd(),
    "repositories"
))

config_instance.SetUrl("http://localhost:5000")

app = flask.Flask(__name__)


@app.route("/<repo>/info/lfs/objects/batch", methods=["POST"])
def batch(repo: str):
    headers = {"Content-Type": "application/vnd.git-lfs+json"}

    repository = Repository("lfs-test")
    request = flask.request.json

    operation = request["operation"]
    transfers = request["transfers"]
    ref = request["ref"]
    objects = request["objects"]

    # build response
    response: Dict[str, Any] = {
        "transfer": "basic"
    }

    if operation == "upload":
        def PrepareUpload(obj: Dict[str, Any]) -> Dict[str, Any]:
            result = {
                **obj
            }

            file_path = repository.GetFilePath(obj["oid"])

            if not file_path.exists():
                result["actions"] = {
                    "upload": {
                        "href": repository.GetFileUrl(obj["oid"])
                    }
                }

            return result

        response["objects"] = list(map(PrepareUpload, objects))
    elif operation == "download":
        def PrepareDownload(obj: Dict[str, Any]) -> Dict[str, Any]:
            result = {
                **obj
            }

            file_path = repository.GetFilePath(obj["oid"])

            if file_path.exists():
                if result["size"] == file_path.stat().st_size:
                    result["actions"] = {
                        "download": {
                            "href": repository.GetFileUrl(obj["oid"])
                        }
                    }
                else:
                    result["error"] = {
                        "code": 404,
                        "message": "Expected size differs from actual size"
                    }
            else:
                result["error"] = {
                    "code": 404,
                    "message": "Object '{}' does not exist".format(obj["oid"])
                }

            return result

        response["objects"] = list(map(PrepareDownload, objects))

    print(json.dumps(response))

    return flask.jsonify(response), 200, headers


@app.route("/<repo>/info/lfs/<oid>", methods=["PUT"])
def upload(repo: str, oid: str):
    repository = Repository(repo)

    file_path = repository.GetFilePath(oid)

    os.makedirs(os.path.dirname(file_path), mode=0o777, exist_ok=True)

    with NamedTemporaryFile(delete=False) as tmp:
        for chunk in FileWrapper(flask.request.stream):
            tmp.write(chunk)

    Path(tmp.name).rename(file_path)

    return flask.jsonify(ok=True)


@app.route("/<repo>/info/lfs/<oid>")
def download(repo: str, oid: str):
    repository = Repository(repo)

    file_path = repository.GetFilePath(oid)

    if not file_path.exists():
        flask.abort(404)

    return flask.helpers.send_file(str(file_path))
