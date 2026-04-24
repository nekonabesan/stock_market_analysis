container_arm ディレクトリは Apple Silicon / ARM（macOS）上で直接ビルド・起動するための Docker 定義を格納します。

使い方（mac のターミナル上で実行）:

# ビルド
cd container_arm
# 普通に docker compose を使う
docker compose build --no-cache

# 起動
docker compose up -d --no-build

備考:
- ta-lib のソースに含まれる autotools の古い config.guess を上書きする処理を `container_arm/api/Dockerfile` と `container_arm/notebook/Dockerfile` に入れています。これは Apple Silicon（aarch64）でのビルド失敗を回避するための最小変更です。
- Dockerfile を編集したくない場合は、`DOCKER_DEFAULT_PLATFORM=linux/amd64` を指定してエミュレーションでビルドする運用も可能ですが遅くなります。
