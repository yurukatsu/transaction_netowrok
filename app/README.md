# App

App作成場

## ディレクトリ

- [steamlit_app][streamlit-app-dir-url]: streamlitで作成したApp

## 実行方法

### 開発時

1. コンテナ（コンテナ名：streamlit_app）を起動する

    ```bash
    docker compose up -d
    ```

2. streamlitサーバー立ち上げ

    ```bash
    docker exec -it streamlit_app /bin/bash
    cd app
    streamlit run homo.py
    ```

3. [localhost:58501](http://localhost:58501)にアクセス

<!-- link -->
[streamlit-app-dir-url]: ./streamlit_app