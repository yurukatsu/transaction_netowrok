# Experiments

実験場

## ディレクトリ

- [notebooks][notebook-dir-url]: ノートブック置き場（実験はメインにここでやることにする）

## 実行方法

1. コンテナ（コンテナ名：netexp）を起動する

    ```bash
    docker compose up -d
    ```

    ここで，コンテナ内のnotebooksディレクトリは[./notebooks][notebook-dir-url]，コンテナ内のdataディレクトリは[../data][data-dir-url]にマウントしている．

2. notebook立ち上げ

    ```bash
    docker exec -it netexp jupyter notebook --ip=0.0.0.0 --allow-root --port=8888 --NotebookApp.token=''
    ```

3. [localhost:8888](http://localhost:8888)にアクセス

<!-- link -->
[notebook-dir-url]: ./notebooks
[data-dir-url]: ../data