from flask import Flask, jsonify, request
import datetime
import io
import sys
import json
import numpy as np
import pickle
import xgboost as xgb
import pandas as pd
import boto3

app = Flask(__name__)
# コードから参照するXGBoostモデルのパス
MODEL_PATH = "./artifact/xgboost_model.pickle"

# リクエストのS3保存先の情報
S3_BUCKET = "apprunner-s3-test"  # バケット名は全AWS内で一意であるため、別の名前を指定する必要があります。
S3_DIR = "requests/"

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
    request_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) #リクエスト時刻

    response = {
        "success": False,
        "Content-Type": "application/json"
    }

    if request.get_json().get("feature"):
        feature = request.get_json().get("feature") # リクエストからfeature読み込み
        
        response["pred"] = model_predict(feature) # model_predict関数を使ってモデル予測
        response["success"] = True

        save_s3(request_time, feature, response["pred"])
        print_result(request_time, feature, response["pred"])

    return jsonify(response)


# XGBoostモデルによる予測を行う関数
def model_predict(feature: list) -> list:
    global model
    feature = np.array(feature)
    app.logger.debug(feature.shape)  # HTTPリクエストのfeatureのnp.ndarrayに変換
    if len(feature.shape) == 1:  # もしデータが1つ、かつ1次元であった場合、featureを2次元へ整形
        feature = feature.reshape((1, -1))
        
    dfeature = xgb.DMatrix(feature)  # XGBoostのデータ形式に変換 
    pred = model.predict(dfeature)  # モデルの予測
    pred_list = pred.tolist()  # 予測結果をpythonのlistに変換

    return pred_list


# リクエストおよびレスポンスを、pd.DataFrame経由でCSVとしてS3に保存する関数
def save_s3(request_time: datetime.datetime, feature: list, pred: list):
    # DataFrameに代入するデータの整理
    request_time_iso = request_time.isoformat() 

    feature = np.array(feature)
    if len(feature.shape) == 1:  # もしデータが1つ、かつ1次元であった場合、featureを2次元へ整形
        feature = feature.reshape((1, -1))
    
    sr_pred = pd.Series(pred)
    
    # 出力するDataFrameの作成
    df = pd.DataFrame(feature, columns=['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8'])
    df['pred'] = sr_pred
    df["request_time"] = request_time_iso

    # dfを、StringIOのバッファを利用して、CSV化＆文字列化する。（ファイルには出力しない。）
    ## 参考リンク：https://dev.classmethod.jp/articles/read-csv-file-on-s3-bucket-into-buffer-and-edit-it-with-pandas/
    buffer_out = io.StringIO()
    df.to_csv(buffer_out, header=True, index=False)
    body_out = buffer_out.getvalue()

    FILE_KEY = S3_DIR + request_time_iso + ".csv"

    obj = s3.Object(S3_BUCKET, FILE_KEY)
    r = obj.put(Body=body_out)
    
    return r


def print_result(request_time: datetime.datetime, feature: list, pred: list):
    """
    リクエストおよびレスポンスを、CloudWatch分析用にprintする関数。
    CloudWatch Logs Insightsを用いて分析しやすいよう、json形式の文字列でprintする。

    参考リンク：https://dev.classmethod.jp/articles/how-to-cloudwatch-logs-insights/
    """
    request_time_iso = request_time.isoformat()
    if check_list_dim(feature) == 1:
        feature = [feature]

    content = dict()
    content["type"] = "RESULT"
    content["request_time"] = request_time_iso

    # 予測結果を、特徴量と予測値のペアに整形する
    predict_list = [{"feature": ftr, "pred": prd} for ftr, prd in zip(feature, pred)]
    content["predict"] = predict_list

    # json文字列への変換
    # text = json.dumps(content, indent=4, separators=(',', ': '))
    text = json.dumps(content)

    # 結果の表示（そのままCloudWatchへ記録される）
    # print(text, file=sys.stderr)
    print(text, flush=True)

    return


def check_list_dim(l: list) -> int:
    l_np = np.array(l)

    return len(l_np.shape)

if __name__ == "__main__":
    app.run()
