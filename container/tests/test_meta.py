import json
import os
import shutil
from typing import Union, List


def setup_inputdata_folder(
    inputdata_name: Union[str, List[str]],
    format_name: str = "jeol_fe",
    case_name: str = "case1",
):
    """テスト用でdataフォルダ群の作成とrawファイルの準備（jeol_maiml用）

    Args:
        inputdata_name (Union[str, List[str]]): rawファイル名
        format_name (str): 使用するフォーマット名（固定: jeol_maiml）
        case_name (str): ケース名（case1 など）
    """

    # <project_root>/data
    destination_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data"
    )

    # ① data フォルダ初期化
    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)

    # ② 必要ディレクトリ作成
    os.makedirs(os.path.join(destination_path, "inputdata"), exist_ok=True)
    os.makedirs(os.path.join(destination_path, "invoice"), exist_ok=True)

    # ③ rawfile のコピー元
    raw_root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "inputdata",
        format_name,
        case_name,
    )

    inputdata_original_path = os.path.join(raw_root, "inputdata")
    invoice_original_path = os.path.join(raw_root, "invoice")

    # ④ inputdata コピー（単一 / 複数対応）
    if isinstance(inputdata_name, list):
        for fname in inputdata_name:
            shutil.copy(
                os.path.join(inputdata_original_path, fname),
                os.path.join(destination_path, "inputdata"),
            )
    else:
        shutil.copy(
            os.path.join(inputdata_original_path, inputdata_name),
            os.path.join(destination_path, "inputdata"),
        )

    # ⑤ invoice.json コピー
    shutil.copy(
        os.path.join(invoice_original_path, "invoice.json"),
        os.path.join(destination_path, "invoice"),
    )

    # ⑥ tasksupport テンプレートを丸ごとコピー
    tasksupport_original_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "templates",
        format_name,
        "tasksupport",
    )
    tasksupport_dest_path = os.path.join(destination_path, "tasksupport")

    shutil.copytree(
        tasksupport_original_path,
        tasksupport_dest_path,
        dirs_exist_ok=True,
    )


class TestMeta1:
    """jeol_fe 形式のマルチファイルテスト"""

    inputdata = [
        "CP_200cycle_x100.zip",
    ]

    def test_setup(self):
        setup_inputdata_folder(
            self.inputdata,
            format_name="jeol_fe",
            case_name="case1",
        )

    def test_metadata_constant(self, setup_main, setup_metadatadef_json):
        metadata = "metadata.json"
        result_metadata_filepath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "meta",
            metadata,
        )

        with open(result_metadata_filepath, encoding="utf-8") as f:
            contents = json.load(f)

        for k in contents["constant"].keys():
            assert setup_metadatadef_json.get(k)

    def test_metadata_variable(self, setup_metadatadef_json):
        metadata = "metadata.json"
        result_metadata_filepath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "meta",
            metadata,
        )

        with open(result_metadata_filepath, encoding="utf-8") as f:
            contents = json.load(f)

        result_variable_keys = [
            k for item in contents["variable"] for k in item.keys()
        ]

        for k in result_variable_keys:
            meta_def = setup_metadatadef_json.get(k)
            variable_flag = setup_metadatadef_json[k].get("variable")

            assert meta_def and variable_flag is not None


class TestMeta2:
    """jeol_maiml 形式のマルチファイルテスト"""

    inputdata = [
        "sem_20250619185355.maiml",
        "sem_20250619185355.txt",
        "sem_20250619185355.bmp"
    ]

    def test_setup(self):
        setup_inputdata_folder(
            self.inputdata,
            format_name="jeol_maiml",
            case_name="case1",
        )

    def test_metadata_constant(self, setup_main, setup_metadatadef_json):
        metadata = "metadata.json"
        result_metadata_filepath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "meta",
            metadata,
        )

        with open(result_metadata_filepath, encoding="utf-8") as f:
            contents = json.load(f)

        for k in contents["constant"].keys():
            assert setup_metadatadef_json.get(k)

    def test_metadata_variable(self, setup_metadatadef_json):
        metadata = "metadata.json"
        result_metadata_filepath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "meta",
            metadata,
        )

        with open(result_metadata_filepath, encoding="utf-8") as f:
            contents = json.load(f)

        result_variable_keys = [
            k for item in contents["variable"] for k in item.keys()
        ]

        for k in result_variable_keys:
            meta_def = setup_metadatadef_json.get(k)
            variable_flag = setup_metadatadef_json[k].get("variable")

            assert meta_def and variable_flag is not None


class TestMeta3:
    """zeiss 形式のマルチファイルテスト"""

    inputdata = [
        "CrossBeam550_自動_1.tif"
    ]

    def test_setup(self):
        setup_inputdata_folder(
            self.inputdata,
            format_name="zeiss",
            case_name="case1",
        )

    def test_metadata_constant(self, setup_main, setup_metadatadef_json):
        metadata = "metadata.json"
        result_metadata_filepath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "meta",
            metadata,
        )

        with open(result_metadata_filepath, encoding="utf-8") as f:
            contents = json.load(f)

        for k in contents["constant"].keys():
            assert setup_metadatadef_json.get(k)

    def test_metadata_variable(self, setup_metadatadef_json):
        metadata = "metadata.json"
        result_metadata_filepath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "meta",
            metadata,
        )

        with open(result_metadata_filepath, encoding="utf-8") as f:
            contents = json.load(f)

        result_variable_keys = [
            k for item in contents["variable"] for k in item.keys()
        ]

        for k in result_variable_keys:
            meta_def = setup_metadatadef_json.get(k)
            variable_flag = setup_metadatadef_json[k].get("variable")

            assert meta_def and variable_flag is not None
