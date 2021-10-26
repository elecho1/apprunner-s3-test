# Apprunner-Flask-XGBoost

Python3 × Flask × Docker x XGBoost推論のサンプル。


## App Runnerへのデプロイ
こちらのページがとても参考になります。  
https://qiita.com/kazama1209/items/b68335cdf45cbddc4835#%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4

App Runnerのデプロイが完了したら、"デフォルトドメイン"にブラウザでアクセスしてみます。  
「XGBoost prediction API with App Runner and flask.」と表示されれば成功です。


## App Runnerへの機械学習API呼び出し
ローカルから、以下のようなPOSTリクエストを送信します。（ここではcurlコマンドを利用しています。）

以下のリクエストにより、1つの入力に対して機械学習の推論を行うことができます。

```
$ curl <App RunnerのデフォルトドメインURL>/api/v1/predict -X POST -H 'Content-Type:application/json' -d '{"feature":[1, 1, 1, 1, 1, 1, 1, 1]}'
```

以下のようなレスポンスを受け取れたら成功です。

```
{"Content-Type":"application/json","pred":[1.7686777114868164],"success":true}
```

また、複数の入力にたいしてまとめて推論を行うこともできます。

```
$ curl <App RunnerのデフォルトドメインURL>/api/v1/predict -X POST -H 'Content-Type:application/json' -d '{"feature":[[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], [1, 1, 1, 1, 1, 1, 1, 1]]}'

{"Content-Type":"application/json","pred":[2.6185295581817627,1.7686777114868164],"success":true}
```

## ローカルでのセットアップ・動作確認
* コンテナをビルド・起動します。
  ```
  $ docker-compose -f docker/docker-compose.yml up -d
  ```
* コンテナが起動しているか確認します。
  [localhost:5000](http://localhost:5000/) にアクセスして「XGBoost prediction API with App Runner and flask.」と返ってくれば成功です。

* 同様にローカルでもAPIの確認を行うことができます。こちらも、"App RunnerのデフォルトドメインURL"を"http://localhost:5000"と置き換えてAPIの呼び出しを行うことができます。

  ```
  $ curl http://localhost:5000/api/v1/predict -X POST -H 'Content-Type:application/json' -d '{"feature":[1, 1, 1, 1, 1, 1, 1, 1]}'
  
  {"Content-Type":"application/json","pred":[1.7686777114868164],"success":true}
  ```

  ```
  $ curl http://localhost:5000/api/v1/predict -X POST -H 'Content-Type:application/json' -d '{"feature":[[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], [1, 1, 1, 1, 1, 1, 1, 1]]}'
  
  {"Content-Type":"application/json","pred":[2.6185295581817627,1.7686777114868164],"success":true}
  ```
  と、JSONが返ってくれば成功です。

* コンテナに入って何かコマンドを打ちたい場合
  ```
  $ docker exec -it flask /bin/ash
  ```
  とコマンドを打って入れます。




## 参考リンク
* 話題のAWS App RunnerをPython3 × Flaskで試してみる:
  https://qiita.com/kazama1209/items/b68335cdf45cbddc4835
* docker関連ファイルをサブディレクトリに配置する:
  https://qiita.com/mogya/items/73d2dae6c429926bf731
* Python(Flask) でサクッと 機械学習 API を作る:
  https://qiita.com/fam_taro/items/1464c42324f15d7b8223
 