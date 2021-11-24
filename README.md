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
1. ローカル環境の環境変数にAWSの認証情報を設定します。（環境変数の設定はセッションごとに行う必要があります。）
    1. **（すでにAWS CLIを利用されている場合）**
        AWS CLIに登録されている認証情報をローカル環境の環境変数にコピーします。  
        ```
        $ export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
        $ export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
        ```
        （オプション：必要に応じて）
        ```
        $ export AWS_SESSION_TOKEN=$(aws configure get aws_session_token)
        ```
    1. **（AWS CLIを利用されていない場合、AWS CLIに認証情報が登録されていない場合）**
        1. AWS認証情報の取得

            こちらのサイトが参考になります。https://qiita.com/n0bisuke/items/1ea245318283fa118f4a

        1. ローカル環境への環境変数の設定

            ```
            $ export AWS_ACCESS_KEY_ID=<上記で取得したAWS_ACCESS_KEY_ID>
            $ export AWS_SECRET_ACCESS_KEY=<上記で取得したAWS_SECRET_ACCESS_KEY>
            ```
            （オプション：必要に応じて）
            ```
            $ export AWS_SESSION_TOKEN=<必要に応じて利用中のAWS_SESSION_TOKEN>
            ```

    **※注意：ベストプラクティスとして、AWSの認証情報をソースコードファイルに記述しないでください！**  
    ファイルにAWS認証情報を記述してしまうとうっかり漏洩してしまうリスクが高まってしまうからです。

1. 上記で設定した認証情報を元に、ローカルでコンテナをセットアップ・起動します。
    ```
    $ docker-compose -f docker/docker-compose.yml run \
    -e AWS_REGION=us-east-1 \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    --service-ports \
    flask
    ```
    （必要に応じて、`-e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \`を追加してください。）

1. （オプション）もしコンテナイメージのリビルドが必要な場合は、以下のコマンドを実行してください。
   ```
   $ docker-compose -f docker/docker-compose.yml build
   ```

1. コンテナが起動しているか確認します。
  [localhost:5000](http://localhost:5000/) にアクセスして「XGBoost prediction API with App Runner and flask.」と返ってくれば成功です。

1. 同様にローカルでもAPIの確認を行うことができます。こちらも、"App RunnerのデフォルトドメインURL"を"http://localhost:5000"と置き換えてAPIの呼び出しを行うことができます。

    コマンド：
    ```
    $ curl http://localhost:5000/api/v1/predict -X POST -H 'Content-Type:application/json' -d '{"feature":[1, 1, 1, 1, 1, 1, 1, 1]}'
    ```
    結果：
    ```
    {"Content-Type":"application/json","pred":[1.7686777114868164],"success":true}
    ```

    コマンド：
    ```
    $ curl http://localhost:5000/api/v1/predict -X POST -H 'Content-Type:application/json' -d '{"feature":[[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], [1, 1, 1, 1, 1, 1, 1, 1]]}'
    ```
    結果：
    ```
    {"Content-Type":"application/json","pred":[2.6185295581817627,1.7686777114868164],"success":true}
    ```
    と、JSONが返ってくれば成功です。

1. （オプション）コンテナに入って何かコマンドを打ちたい場合
    ```
    $ docker exec -it flask /bin/bash
    ```
    とコマンドを打って入れます。




## 参考リンク
* 話題のAWS App RunnerをPython3 × Flaskで試してみる:
  https://qiita.com/kazama1209/items/b68335cdf45cbddc4835
* docker関連ファイルをサブディレクトリに配置する:
  https://qiita.com/mogya/items/73d2dae6c429926bf731
* Python(Flask) でサクッと 機械学習 API を作る:
  https://qiita.com/fam_taro/items/1464c42324f15d7b8223
 