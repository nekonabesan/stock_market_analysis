container_arm ディレクトリは Apple Silicon / ARM（macOS）上で直接ビルド・起動するための Docker 定義を格納します。

使い方（mac のターミナル上で実行）:

# ビルド
cd container_arm
# 普通に docker compose を使う
docker compose build --no-cache

# 起動
docker compose up -d --no-build

Makefile に定義された主要コマンド
- `make build`           : イメージを再ビルドします（--no-cache）。
- `make build-clean`     : イメージ・コンテナ・ボリュームを破棄して再ビルドします（破壊的）。
- `make start`           : 既存イメージでコンテナを起動します（--no-build）。
- `make stop`            : コンテナを停止・削除します。
- `make logs`            : コンテナのログをフォロー表示します。

- `make migrate`         : `alembic revision --autogenerate -m "$(MIGRATION_MSG)"` を実行し、続けて `alembic upgrade head` でマイグレーションを適用します。

- `make revision`        : 差分ファイル（`backend/migrations/versions` 配下）を自動生成します（`MIGRATION_MSG` 環境変数でメッセージ指定可）。
- `make upgrade`         : `alembic upgrade head` を実行します（生成済みマイグレーションを DB に適用）。
- `make downgrade`       : 1 ステップ分ダウングレードします（`alembic downgrade -1`）。
- `make alembic-current` : 現在の DB に記録された Alembic リビジョンを表示します。
- `make alembic-history` : Alembic の履歴（`alembic history --verbose`）を表示します。

- `make seed`            : シードデータを投入します（`python -m seeds.run`）。
- `make init`            : バッチ初期化タスクを実行します（`python -m app.batch.init_market_data`）。
- `make test`            : テストを実行します（`pytest` を API コンテナ内で実行）。

使い方の例（モデルを変更してマイグレーションを作る開発フロー）:
1. ホストでモデルを編集（`backend/app` を修正）
2. `make build`（イメージを再ビルド）または開発時は `docker-compose up -d api`（ホストをマウントしている場合）
3. 差分ファイルを生成: `make revision MIGRATION_MSG="describe change"`
4. 生成されたファイルを確認・必要なら編集（`backend/migrations/versions/*.py`）
5. マイグレーション適用: `make upgrade` または `make migrate`

備考:
- ta-lib のソースに含まれる autotools の古い config.guess を上書きする処理を `container_arm/api/Dockerfile` と `container_arm/notebook/Dockerfile` に入れています。これは Apple Silicon（aarch64）でのビルド失敗を回避するための最小変更です。
- Dockerfile を編集したくない場合は、`DOCKER_DEFAULT_PLATFORM=linux/amd64` を指定してエミュレーションでビルドする運用も可能ですが遅くなります。

## Colima を使う（macOS / Apple Silicon）

Apple Silicon（M1/M2 等）上でローカル Docker 環境を軽量に動かす場合、`colima` を利用すると便利です。以下はよく使う手順です。

- インストール（Homebrew がある前提）:

```bash
brew install colima docker
# または Docker Desktop を利用する場合
brew install --cask docker
```

- Colima の起動:

```bash
# デフォルト起動
colima start

# リソースを指定して起動（例）
colima start --cpu 4 --memory 8 --disk 60
```

- 状態確認 / トラブルシュート:

```bash
colima status
docker info
ls -l ~/.colima/default/docker.sock
```

- 注意点:
	- make や `docker compose` / `docker-compose` を使う前に `colima start` を実行して Docker デーモンを立ち上げてください。エラーメッセージにある「Cannot connect to the Docker daemon at unix:///Users/.../.colima/default/docker.sock」は Colima が起動していない状態で発生します。
	- 古い `docker-compose`（Python ベースの独立バイナリ）を使っている場合は `brew install docker-compose` が必要になることがあります。可能なら `docker compose`（Docker CLI プラグイン）を使ってください。
	- Colima はデフォルトで Apple Silicon に最適なアーキテクチャを使用しますが、特定のイメージを amd64 で動かしたい場合は Colima の設定や `--arch` オプションで調整してください。

起動後に `docker info` が正常に出力されれば、`cd container_arm` して `make start` を再度実行できます。
