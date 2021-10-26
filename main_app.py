from flask import Flask, jsonify, request
import json
import numpy as np
import pickle
import xgboost as xgb
import boto3

app = Flask(__name__)
MODEL_PATH = "./artifact/xgboost_model.pickle"
S3_BUCKET = "apprunner-s3-test"
JSON_KEY = "response.json"

s3 = boto3.resource('s3')


# この部分で、pickle形式のモデルの読み込みを行う
def load_artifact(filename):
    artifact = None
    with open(filename, mode='rb') as fp:
        artifact = pickle.load(fp)
    if artifact is None:
        raise ValueError        
    return artifact

model = load_artifact(MODEL_PATH)

# "http://<ドメイン名>"へアクセスしたときのブラウザ表示
@app.route("/")
def index():
    return "XGBoost prediction API with App Runner and flask."

# "http://<ドメイン名>/api/v1/predict"へAPI呼び出しを行う際の動作
@app.route("/api/v1/predict", methods=["POST"])
def predict():
    response = {
        "success": False,
        "Content-Type": "application/json"
    }

    if request.get_json().get("feature"):
        feature = request.get_json().get("feature") # リクエストからfeature読み込み
        
        response["pred"] = model_predict(feature) # model_predict関数を使ってモデル予測
        response["success"] = True

        r = save_s3(response)
        print(r)

    return jsonify(response)


def model_predict(feature):
    global model
    feature = np.array(feature)
    app.logger.debug(feature.shape)  # HTTPリクエストのfeatureのnp.ndarrayに変換
    if len(feature.shape) != 2:  # もしデータが1つ（=1次元）であった場合
        feature = feature.reshape((1, -1))
        
    dfeature = xgb.DMatrix(feature)  # XGBoostのデータ形式に変換 
    pred = model.predict(dfeature)  # モデルの予測
    pred_list = pred.tolist()  # 予測結果をpythonのlistに変換

    return pred_list


def save_s3(response):
    text = json.dumps(response)

    obj = s3.Object(S3_BUCKET, JSON_KEY)
    r = obj.put(Body=text)
    
    return r


if __name__ == "__main__":
    app.run()
