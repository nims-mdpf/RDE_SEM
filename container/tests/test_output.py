import os
import shutil
from typing import Union, List


def setup_inputdata_folder(
    inputdata_name: Union[str, List[str]],
    format_name: str = "jeol_fe",
    case_name: str = "case1",
):
    """テスト用でdataフォルダ群の作成とrawファイルの準備

    Args:
        inputdata_name (Union[str, List[str]]): rawファイル名
        format_name (str): 使用するフォーマット名（jeol_fe, zeissなど）
        case_name (str): case名（case1 など）
    """

    # destination: <project_root>/data
    destination_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data"
    )
    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)

    os.makedirs(os.path.join(destination_path, "inputdata"), exist_ok=True)
    os.makedirs(os.path.join(destination_path, "invoice"), exist_ok=True)

    # rawfile root
    raw_root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "inputdata",
        format_name,
        case_name,
    )

    inputdata_original_path = os.path.join(raw_root, "inputdata")
    invoice_original_path = os.path.join(raw_root, "invoice")

    # inputdata コピー
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

    # invoice コピー
    shutil.copy(
        os.path.join(invoice_original_path, "invoice.json"),
        os.path.join(destination_path, "invoice"),
    )

    tasksupport_original_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "templates",
        format_name,
        "tasksupport",
    )
    tasksupport_dest_path = os.path.join(destination_path, "tasksupport")
    os.makedirs(tasksupport_dest_path, exist_ok=True)

    for fname in os.listdir(tasksupport_original_path):
        src = os.path.join(tasksupport_original_path, fname)
        dst = os.path.join(tasksupport_dest_path, fname)

        if os.path.isfile(src):
            shutil.copy(src, dst)


class TestOutputCase1:
    """case1
    マルチファイルのテスト: インボイスモード
        "sem_20250619185355.maiml"
        "sem_20250619185355.txt"
        "sem_20250619185355.bmp"

    """

    inputdata: Union[str, List[str]] = [
        "sem_20250619185355.maiml",
        "sem_20250619185355.txt",
        "sem_20250619185355.bmp"
    ]

    def test_setup(self):
        setup_inputdata_folder(self.inputdata, format_name="jeol_maiml", case_name="case1")

    def test_raw_data(self, setup_main, data_path):
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "sem_20250619185355.maiml"))
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "sem_20250619185355.txt"))
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "sem_20250619185355.bmp"))

    def test_main_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "main_image", "sem_20250619185355.png"))

    def test_thumbnail(self, data_path):
        assert os.path.exists(os.path.join(data_path, "thumbnail", "sem_20250619185355.png"))

    def test_meta(self, data_path):
        assert os.path.exists(os.path.join(data_path, "meta", "metadata.json"))


class TestOutputCase2:
    """case2
    マルチファイルのテスト: インボイスモード
        "CP_200cycle_x100.zip"

    """

    inputdata: Union[str, List[str]] = [
        "CP_200cycle_x100.zip"
    ]

    def test_setup(self):
        setup_inputdata_folder(self.inputdata, format_name="jeol_fe", case_name="case1")

    def test_raw_data(self, setup_main, data_path):
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "CP_200cycle_x100.tif"))
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "CP_200cycle_x100.txt"))

    def test_main_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "main_image", "CP_200cycle_x100.png"))

    def test_thumbnail(self, data_path):
        assert os.path.exists(os.path.join(data_path, "thumbnail", "CP_200cycle_x100.png"))

    def test_meta(self, data_path):
        assert os.path.exists(os.path.join(data_path, "meta", "metadata.json"))


class TestOutputCase3:
    """case3
    マルチファイルのテスト: マルチデータタイルモード
        "CrossBeam550_自動_1.tif",
        "CrossBeam1540EsB_1.tif",

    """

    inputdata: Union[str, List[str]] = [
        "CrossBeam550_自動_1.tif",
        "CrossBeam1540EsB_1.tif",
    ]

    def test_setup(self):
        setup_inputdata_folder(self.inputdata, format_name="zeiss", case_name="case1")

    def test_raw_data(self, setup_main, data_path):
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "CrossBeam1540EsB_1.tif"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "nonshared_raw", "CrossBeam550_自動_1.tif"))

    def test_main_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "main_image", "CrossBeam1540EsB_1.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "main_image", "CrossBeam550_自動_1.png"))

    def test_thumbnail(self, data_path):
        assert os.path.exists(os.path.join(data_path, "thumbnail", "CrossBeam1540EsB_1.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "thumbnail", "CrossBeam550_自動_1.png"))

    def test_meta(self, data_path):
        assert os.path.exists(os.path.join(data_path, "meta", "metadata.json"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "meta", "metadata.json"))


class TestOutputCase4:
    """case4
    マルチファイルのテスト: スマートテーブルモード
        "sem_20250619185355.maiml"
        "sem_20250619185355.bmp"
        "sem_20250619185355-1.maiml"
        "sem_20250619185355-1.bmp"

    """

    inputdata: Union[str, List[str]] = [
        "sem_20250619185355.zip",
        "smarttable_SEM.xlsx"
    ]

    def test_setup(self):
        setup_inputdata_folder(self.inputdata, format_name="jeol_maiml", case_name="case2")

    def test_raw_data(self, setup_main, data_path):
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "sem_20250619185355-1.maiml"))
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "sem_20250619185355-1.bmp"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "nonshared_raw", "sem_20250619185355.maiml"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "nonshared_raw", "sem_20250619185355.bmp"))

    def test_main_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "main_image", "sem_20250619185355-1.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "main_image", "sem_20250619185355.png"))

    def test_thumbnail(self, data_path):
        assert os.path.exists(os.path.join(data_path, "thumbnail", "sem_20250619185355-1.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "thumbnail", "sem_20250619185355.png"))

    def test_meta(self, data_path):
        assert os.path.exists(os.path.join(data_path, "meta", "metadata.json"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "meta", "metadata.json"))


class TestOutputCase5:
    """case5
    マルチファイルのテスト: スマートテーブルモード
        "CP_200cycle_x100.tif"
        "CP_200cycle_x100.txt"
        "test1.jpg"
        "test1.txt"
    """

    inputdata: Union[str, List[str]] = [
        "summary.zip",
        "smarttable_SEM.xlsx"
    ]

    def test_setup(self):
        setup_inputdata_folder(self.inputdata, format_name="jeol_fe", case_name="case2")

    def test_raw_data(self, setup_main, data_path):
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "test1.jpg"))
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "test1.txt"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "nonshared_raw", "CP_200cycle_x100.txt"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "nonshared_raw", "CP_200cycle_x100.tif"))

    def test_main_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "main_image", "test1.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "main_image", "CP_200cycle_x100.png"))

    def test_thumbnail(self, data_path):
        assert os.path.exists(os.path.join(data_path, "thumbnail", "test1.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "thumbnail", "CP_200cycle_x100.png"))

    def test_meta(self, data_path):
        assert os.path.exists(os.path.join(data_path, "meta", "metadata.json"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "meta", "metadata.json"))


class TestOutputCase6:
    """case5
    マルチファイルのテスト: マルチデータタイルモード
        "CP_200cycle_x100.tif"
        "CP_200cycle_x100.txt"
        "test1.jpg"
        "test1.txt"
    """

    inputdata: Union[str, List[str]] = [
        "CP_200cycle_x100.zip",
        "test1.zip"
    ]

    def test_setup(self):
        setup_inputdata_folder(self.inputdata, format_name="jeol_fe", case_name="case3")

    def test_raw_data(self, setup_main, data_path):
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "CP_200cycle_x100.tif"))
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "CP_200cycle_x100.txt"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "nonshared_raw", "test1.jpg"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "nonshared_raw", "test1.txt"))

    def test_main_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "main_image", "CP_200cycle_x100.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "main_image", "test1.png"))

    def test_thumbnail(self, data_path):
        assert os.path.exists(os.path.join(data_path, "thumbnail", "CP_200cycle_x100.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "thumbnail", "test1.png"))

    def test_meta(self, data_path):
        assert os.path.exists(os.path.join(data_path, "meta", "metadata.json"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "meta", "metadata.json"))


class TestOutputCase7:
    """case3
    マルチファイルのテスト: スマートテーブルモード
        "Helios 5_1.tif",
        "HeliosG4.tif"

    """

    inputdata: Union[str, List[str]] = [
        "smarttable_SEM.xlsx",
        "zeiss.zip",
    ]

    def test_setup(self):
        setup_inputdata_folder(self.inputdata, format_name="zeiss", case_name="case3")

    def test_raw_data(self, setup_main, data_path):
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "CrossBeam550_自動_1.tif"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "nonshared_raw", "CrossBeam1540EsB_1.tif"))

    def test_main_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "main_image", "CrossBeam550_自動_1.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "main_image", "CrossBeam1540EsB_1.png"))

    def test_thumbnail(self, data_path):
        assert os.path.exists(os.path.join(data_path, "thumbnail", "CrossBeam550_自動_1.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "thumbnail", "CrossBeam1540EsB_1.png"))

    def test_meta(self, data_path):
        assert os.path.exists(os.path.join(data_path, "meta", "metadata.json"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "meta", "metadata.json"))


class TestOutputCase8:
    """case3
    マルチファイルのテスト: スマートテーブルモード
        "CrossBeam550_自動_1.tif",
        "CrossBeam1540EsB_1.tif",

    """

    inputdata: Union[str, List[str]] = [
        "smarttable_SEM.xlsx",
        "thermo_fisher.zip",
    ]

    def test_setup(self):
        setup_inputdata_folder(self.inputdata, format_name="thermo_fisher", case_name="case3")

    def test_raw_data(self, setup_main, data_path):
        assert os.path.exists(os.path.join(data_path, "nonshared_raw", "HeliosG4.tif"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "nonshared_raw", "Helios 5_1.tif"))

    def test_main_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "main_image", "HeliosG4.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "main_image", "Helios 5_1.png"))

    def test_thumbnail(self, data_path):
        assert os.path.exists(os.path.join(data_path, "thumbnail", "HeliosG4.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "thumbnail", "Helios 5_1.png"))

    def test_meta(self, data_path):
        assert os.path.exists(os.path.join(data_path, "meta", "metadata.json"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "meta", "metadata.json"))
