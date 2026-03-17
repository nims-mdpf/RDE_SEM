# SEM用テンプレート

## 概要
SEMをご利用の方に適したテンプレートです。以下のバリエーションが提供されています。
- DT0021
    - JEOL_maiml
- DT0022
    - JEOL_fe
- DT0023
    - TIFF_EXIF

SEMの専門家によって監修されたメタ情報を上記ファイルから自動的にRDEが抽出します。 プロットは登録SEM画像を出力します。
- JEOLのMaiML/TXT形式、ZEISSおよびThermo Fisher ScientificのTIFF形式に対応したメタ情報の抽出、SEM画像の登録を行う。
- JEOL_maimlテンプレートとTIFF_EXIFテンプレートのみMultiDataTileモード対応
- 全テンプレートでSmartTableにモード対応
- マジックネーム対応（データ名を${filename}とすると、ファイル名をデータ名にマッピングする）

## メタ情報
- [メタ情報](docs/requirement_analysis/要件定義.xlsx)

## 基本情報

### コンテナ情報
- 【コンテナ名】rdecontreg.azurecr.io/nims/mdpf_shared/nims_mdpf_shared_sem:v1.0

### テンプレート情報
- DT0021:
    - 【データセットテンプレートID】NIMS_DT0021_SEM_JEOL_maiml_v1.0
    - 【データセットテンプレート名日本語】SEM JEOL maiml データセットテンプレート
    - 【データセットテンプレート名英語】SEM JEOL maiml dataset-template
    - 【データセットテンプレートの説明】JEOLのSEMをご利用の方に適したモードです。MaiML形式でデータを取得されている方がご利用いただけます。 SEMの専門家によって監修されたメタ情報をmaimlファイルから自動的に抽出し格納します。maimlファイル中に記載されたresultTemplate_semResultImage に記載された画像ファイルを代表画像として登録します。
    - 【バージョン】1.0
    - 【データセット種別】加工・計測レシピ型
    - 【データ構造化】あり (システム上「あり」を選択)
    - 【取り扱い事業】NIMS研究および共同研究プロジェクト (PROGRAM)
    - 【装置名】(なし。装置情報を紐づける場合はこのテンプレートを複製し、装置情報を設定すること。)

- DT0022:
    - 【データセットテンプレートID】NIMS_DT0022_SEM_JEOL_fe_v1.0
    - 【データセットテンプレート名日本語】SEM JEOL fe データセットテンプレート
    - 【データセットテンプレート名英語】SEM JEOL fe dataset-template
    - 【データセットテンプレートの説明】JEOLのSEMをご利用の方に適したモードです。txtフォーマットでデータを取得されている方がご利用いただけます。 SEMの専門家によって監修されたメタ情報をtxtファイルから自動的に抽出し格納します。SEM画像とtxt形式のメタ情報の2ファイルを拡張子以外は同一にして組にし、zip化して登録します。
    - 【バージョン】1.0
    - 【データセット種別】加工・計測レシピ型
    - 【データ構造化】あり (システム上「あり」を選択)
    - 【取り扱い事業】NIMS研究および共同研究プロジェクト (PROGRAM)
    - 【装置名】(なし。装置情報を紐づける場合はこのテンプレートを複製し、装置情報を設定すること。)

- DT0023:
    - 【データセットテンプレートID】NIMS_DT0023_SEM_TIFF_EXIF_v1.0
    - 【データセットテンプレート名日本語】SEM TIFF_EXIF データセットテンプレート
    - 【データセットテンプレート名英語】SEM TIFF_EXIF dataset-template
    - 【データセットテンプレートの説明】ZEISSおよびThermo Fisher Scientific製のSEMをご利用の方に適したモードです。TIFF形式でデータを取得している方にご利用いただけます。SEMの専門家が監修したメタ情報をtifファイルから自動的に抽出し格納します。熱間圧延によるSEM（走査型電子顕微鏡）画像を、構造化処理に適した形式で扱うためのデータセットテンプレートです。
    - 【バージョン】1.0
    - 【データセット種別】加工・計測レシピ型
    - 【データ構造化】あり (システム上「あり」を選択)
    - 【取り扱い事業】NIMS研究および共同研究プロジェクト (PROGRAM)
    - 【装置名】(なし。装置情報を紐づける場合はこのテンプレートを複製し、装置情報を設定すること。)

### データ登録方法
- 送り状画面をひらいて入力ファイルに関する情報を入力する
- 「登録ファイル」欄に登録したいファイルをドラッグアンドドロップする。
  - 複数のファイルを入力し一度に複数のデータを登録することが可能。
  - 複数のファイルを入力する場合は、「データ名」に「${filename}」と入力し「データ名」に入力ファイル名をマッピングさせることができる
- 「登録開始」ボタンを押して（確認画面経由で）登録を開始する

## 構成

### レポジトリ構成

```
sem
├── README.md
├── container
│   ├── Dockerfile
│   ├── Dockerfile_nims
│   ├── data (入出力データ)
│   ├── main.py
│   ├── modules (共通ソースコード)
│   │   ├── __init__.py
│   │   └── datasets_process.py (構造化処理の大元)
│   ├── modules_sem (SEM向けソースコード)
│   │   ├── JEOL
│   │   │   ├── __init__.py
│   │   │   ├── maiml_img (MaiML形式用)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── inputfile_handler.py (入力ファイル読み込み)
│   │   │   │   └── mapping_csv.py (マッピングCSV処理)
│   │   │   └── txt_img (テキスト画像フォーマット用)
│   │   │       ├── __init__.py
│   │   │       ├── inputfile_handler.py (入力ファイル読み込み)
│   │   │       └── mapping_csv.py (マッピングCSV処理)
│   │   ├── TIFF_EXIF (TIF形式用)
│   │   │   ├── Thermo_Fisher
│   │   │   │   ├── __init__.py
│   │   │   │   └── tif_exif_handler.py (TIF EXIF解析)
│   │   │   ├── ZEISS
│   │   │   │   ├── __init__.py
│   │   │   │   └── tif_exif_handler.py (TIF EXIF解析)
│   │   │   ├── inputfile_handler.py (入力ファイル読み込み)
│   │   │   └── mapping_csv.py (マッピングCSV処理)
│   │   ├── __init__.py
│   │   ├── factory.py (設定ファイル、使用クラス取得)
│   │   ├── graph_handler.py (グラフ描画)
│   │   ├── inputfile_handler.py (共通入力ファイル処理)
│   │   ├── interfaces.py
│   │   ├── mapping_handler.py (マッピング処理)
│   │   ├── meta_handler.py (メタデータ解析)
│   │   ├── structured_handler.py (構造化データ解析)
│   │   └── tif_exif_handler.py (TIF EXIF解析)
│   ├── pip.conf
│   ├── pyproject.toml
│   ├── requirements-test.txt
│   ├── requirements.txt
│   └── tests (テストコード)
├── docs (ドキュメント)
│   ├── mkdoc_ci_scripts.py
│   └── template
│       └── README.md
├── inputdata (サンプルデータ)
│   ├── jeol_fe (JEOL FE向け)
│   ├── jeol_maiml (JEOL MAIML向け)
│   ├── thermo_fisher (Thermo Fisher Scientific向け)
│   └── zeiss (ZEISS向け)
└── templates (テンプレート群)
    ├── jeol_fe (JEOL FE向け)
    │   ├── batch.yaml
    │   ├── catalog.schema.json (カタログ項目定義)
    │   ├── invoice.schema.json (送り状項目定義)
    │   ├── jobs.template.yaml
    │   ├── metadata-def.json (メタデータ定義)
    │   └── tasksupport
    │       ├── invoice.schema.json
    │       ├── mapping.csv
    │       ├── metadata-def.json
    │       └── rdeconfig.yaml (設定ファイル)
    ├── jeol_maiml (JEOL MAIML向け)
    │   ├── batch.yaml
    │   ├── catalog.schema.json
    │   ├── invoice.schema.json
    │   ├── jobs.template.yaml
    │   ├── metadata-def.json
    │   └── tasksupport
    │       ├── invoice.schema.json
    │       ├── mapping.csv
    │       ├── metadata-def.json
    │       └── rdeconfig.yaml
    ├── thermo_fisher (Thermo Fisher Scientific向け)
    │   ├── batch.yaml
    │   ├── catalog.schema.json
    │   ├── invoice.schema.json
    │   ├── jobs.template.yaml
    │   ├── metadata-def.json
    │   └── tasksupport
    │       ├── invoice.schema.json
    │       ├── mapping.csv
    │       ├── metadata-def.json
    │       └── rdeconfig.yaml
    └── zeiss (ZEISS向け)
        ├── batch.yaml
        ├── catalog.schema.json
        ├── invoice.schema.json
        ├── jobs.template.yaml
        ├── metadata-def.json
        └── tasksupport
            ├── invoice.schema.json
            ├── mapping.csv
            ├── metadata-def.json
            └── rdeconfig.yaml
```

### 動作環境ファイル入出力
- DT0021
```
container/data
├── attachment
├── inputdata
│   ├── sem_20250619185355.bmp (入力データ)
│   └── sem_20250619185355.maiml (入力データ)
├── invoice
│   └── invoice.json (送り状ファイル)
├── logs
│   └── rdesys.log (RDEシステムログ)
├── main_image
│   └── sem_20250619185355.png ((メイン)プロット画像)
├── meta
│   └── metadata.json (主要パラメータメタ情報ファイル)
├── nonshared_raw
│   ├── sem_20250619185355.bmp (入力データコピー)
│   └── sem_20250619185355.maiml (入力データコピー)
├── tasksupport (テンプレート群)
│   ├── invoice.schema.json (送り状項目定義)
│   ├── mapping.csv (マッピング定義)
│   ├── metadata-def.json (メタデータ定義)
│   └── rdeconfig.yaml (設定ファイル)
└── thumbnail
    └── sem_20250619185355.png (サムネイル用プロット画像)

```

- DT0022
```
container/data
├── attachment
├── inputdata
│   ├── CP_200cycle_x100.tif (登録ファイル欄にドラッグアンドドロップした任意のファイル)
│   └── CP_200cycle_x100.txt (登録ファイル欄にドラッグアンドドロップした任意のファイル)
├── invoice
│   └── invoice.json (送り状ファイル)
├── logs
│   └── rdesys.log (RDEシステムログ)
├── main_image
│   └── CP_200cycle_x100.png ((メイン)プロット画像)
├── meta
│   └── metadata.json (主要パラメータメタ情報ファイル)
├── nonshared_raw
│   ├── CP_200cycle_x100.tif (入力データコピー)
│   └── CP_200cycle_x100.txt (入力データコピー)
├── tasksupport (テンプレート群)
│   ├── invoice.schema.json (送り状項目定義)
│   ├── mapping.csv (マッピング定義)
│   ├── metadata-def.json (メタデータ定義)
│   └── rdeconfig.yaml (設定ファイル)
└── thumbnail
    └── CP_200cycle_x100.png (サムネイル用プロット画像)

```

- DT0023
```
container/data
├── attachment
├── inputdata
│   └── CrossBeam1540EsB_1.tif (登録ファイル欄にドラッグアンドドロップした任意のファイル)
├── invoice
│   └── invoice.json (送り状ファイル)
├── logs
│   └── rdesys.log (RDEシステムログ)
├── main_image
│   └── CrossBeam1540EsB_1.png ((メイン)プロット画像)
├── meta
│   └── metadata.json (主要パラメータメタ情報ファイル)
├── nonshared_raw
│   └── CrossBeam1540EsB_1.tif (入力データコピー)
├── structured
│   └── tif_info.json (前処理した計測データやメタ情報)
├── tasksupport (テンプレート群)
│   ├── invoice.schema.json (送り状項目定義)
│   ├── mapping.csv (マッピング定義)
│   ├── metadata-def.json (メタデータ定義)
│   └── rdeconfig.yaml (設定ファイル)
└── thumbnail
    └── CrossBeam1540EsB_1.png (サムネイル用プロット画像)

```

## データ閲覧
- データ一覧画面を開く。
- ギャラリー表示タブでは１データがタイル状に並べられている。データ名をクリックして詳細を閲覧する。
- ツリー表示タブではタクソノミーにしたがってデータを階層表示する。データ名をクリックして詳細を閲覧する。

### 動作環境
- Python: 3.12
- RDEToolKit: 1.6.1