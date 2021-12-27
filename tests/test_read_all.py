import pytest

import exomole
from exomole.exceptions import AllParseError, AllParseWarning, LineWarning
from exomole.read_all import AllParser, Molecule, Isotopologue
from . import resources_path

example_all_path = resources_path.joinpath("exomol_data", "exomol.all")

with open(example_all_path, "r") as fp:
    example_all_raw_text = fp.read()


def test_dataclasses_repr():
    assert (
        repr(
            Isotopologue(
                inchi_key="inchi_key",
                iso_slug="iso_slug",
                iso_formula="iso_formula",
                dataset_name="dataset_name",
                version=42,
            )
        )
        == "Isotopologue(iso_slug)"
    )
    assert (
        repr(Molecule(names=["name"], formula="formula", isotopologues={}))
        == "Molecule(formula)"
    )


def test_instantiation_path():
    all_parser = AllParser(example_all_path)
    assert all_parser.raw_text == example_all_raw_text
    assert all_parser.file_name == example_all_path.name


def test_instantiation_api(monkeypatch):
    monkeypatch.setattr(
        exomole.read_all,
        "get_file_raw_text_over_api",
        lambda which: "foo",
    )
    assert AllParser().raw_text == "foo"


def test_parse_exomol_all():
    all_parser = AllParser(example_all_path)
    all_parser.parse(warn_on_comments=False)

    # parsed attributes:
    assert all_parser.id == "EXOMOL.master"
    assert all_parser.version == 20210707
    assert all_parser.num_molecules == 80
    assert all_parser.num_isotopologues == 193
    assert all_parser.num_datasets == 68
    assert len(all_parser.molecules) == 80
    assert [
        mol_formula for mol_formula in all_parser.molecules["H2O"].isotopologues
    ] == ["(1H)2(16O)", "(1H)2(17O)", "(1H)2(18O)", "(1H)(2H)(16O)", "(2H)2(16O)"]


def test_invalid_molecule_formula(monkeypatch):
    monkeypatch.setattr(
        exomole.read_all,
        "get_file_raw_text_over_api",
        lambda x: example_all_raw_text.replace("H2O ", "foo2loo "),
    )
    all_parser = AllParser()
    with pytest.raises(AllParseError):
        all_parser.parse(warn_on_comments=False)


def test_invalid_isotopologue_formula(monkeypatch):
    monkeypatch.setattr(
        exomole.read_all,
        "get_file_raw_text_over_api",
        lambda x: example_all_raw_text.replace("(1H)(2H)(16O) ", "spam "),
    )
    all_parser = AllParser()
    with pytest.raises(AllParseError):
        all_parser.parse(warn_on_comments=False)


def test_invalid_line_value_type(monkeypatch):
    monkeypatch.setattr(
        exomole.read_all,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_all_raw_text.replace("   1", "   a"),
    )
    all_parser = AllParser()
    with pytest.raises(AllParseError, match=".*Unexpected value type*"):
        all_parser.parse(warn_on_comments=False)


def test_invalid_line_format(monkeypatch):
    monkeypatch.setattr(
        exomole.read_all,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_all_raw_text.replace("# Iso-slug", "Iso-slug"),
    )
    all_parser = AllParser()
    with pytest.raises(AllParseError, match=".*Unexpected line format*"):
        all_parser.parse(warn_on_comments=False)


def test_warn_on_comments(monkeypatch):
    monkeypatch.setattr(
        exomole.read_all,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_all_raw_text,
    )
    all_parser = AllParser()
    # should not warn, the raw text is all sorted
    with pytest.warns(None) as record:
        all_parser.parse(warn_on_comments=True)
    assert not record
    all_parser.raw_text = example_all_raw_text.replace("# Iso-slug", "# Unexpected!")
    with pytest.warns(LineWarning):
        all_parser.parse(warn_on_comments=True)
    with pytest.warns(None) as record:
        all_parser.parse(warn_on_comments=False)
    assert not record


def test_warn_on_duplicate_isotopologue(monkeypatch):
    monkeypatch.setattr(
        exomole.read_all,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_all_raw_text.replace(
            "(1H)2(17O)", "(1H)2(16O)"
        ),
    )
    all_parser = AllParser()
    with pytest.warns(AllParseWarning, match=".*more than one dataset.*"):
        all_parser.parse(warn_on_comments=False)
    with pytest.warns(AllParseWarning, match=".*more than one dataset.*"):
        all_parser.parse(warn_on_comments=True)


def test_warn_on_number_isotopologues(monkeypatch):
    monkeypatch.setattr(
        exomole.read_all,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_all_raw_text.replace(" 193", " 194"),
    )
    all_parser = AllParser()
    with pytest.warns(AllParseWarning, match=".*Number of isotopologues*"):
        all_parser.parse(warn_on_comments=False)
    with pytest.warns(AllParseWarning, match=".*Number of isotopologues*"):
        all_parser.parse(warn_on_comments=True)


def test_warn_on_number_datasets(monkeypatch):
    monkeypatch.setattr(
        exomole.read_all,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_all_raw_text.replace("  68", " 69"),
    )
    all_parser = AllParser()
    with pytest.warns(AllParseWarning, match=".*Number of datasets*"):
        all_parser.parse(warn_on_comments=False)
    with pytest.warns(AllParseWarning, match=".*Number of datasets*"):
        all_parser.parse(warn_on_comments=True)


def test_unexpected_file_id(monkeypatch):
    monkeypatch.setattr(
        exomole.read_all,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_all_raw_text.replace(
            "EXOMOL.master", "EXOMOL.all"
        ),
    )
    all_parser = AllParser()
    with pytest.raises(AllParseError, match=".*Unexpected ID*"):
        all_parser.parse(warn_on_comments=False)
