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
