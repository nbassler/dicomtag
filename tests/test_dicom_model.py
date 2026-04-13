import pytest
from pathlib import Path
from dicomtag.model.dicom_model import DICOMDataModel

SAMPLE_DCM = Path(__file__).parent.parent / "resources" / "Plan5.5.dcm"


@pytest.fixture
def model():
    return DICOMDataModel()


@pytest.fixture
def loaded_model():
    m = DICOMDataModel()
    m.load_dicom_file(str(SAMPLE_DCM))
    return m


def test_initial_state(model):
    assert model.dicom_data is None
    assert model.filename is None


def test_load_file(loaded_model):
    assert loaded_model.dicom_data is not None
    assert loaded_model.filename is not None


def test_load_nonexistent_file(model):
    model.load_dicom_file("nonexistent.dcm")
    assert model.dicom_data is None


def test_get_all_tags(loaded_model):
    tags = loaded_model.get_all_tags()
    assert len(list(tags)) > 0


def test_clear_data(loaded_model):
    loaded_model.clear_data()
    assert loaded_model.dicom_data is None
    assert loaded_model.filename is None


def test_save_file(loaded_model, tmp_path):
    out = tmp_path / "output.dcm"
    result = loaded_model.save_dicom_file(str(out))
    assert result is True
    assert out.exists()


def test_save_without_data(model, tmp_path):
    result = model.save_dicom_file(str(tmp_path / "output.dcm"))
    assert result is False
