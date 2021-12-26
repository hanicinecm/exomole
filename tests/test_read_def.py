import math

import pytest

import exomole
from exomole.exceptions import DefParseError, LineWarning
from exomole.read_def import DefParser, Isotope, QuantumCase, Quantum
from . import resources_path

example_def_path = resources_path.joinpath(
    "exomol_data", "CaH", "40Ca-1H", "Yadin", "40Ca-1H__Yadin.def"
)

with open(example_def_path, "r") as fp:
    example_def_raw_text = fp.read()


def test_instantiation_path():
    def_parser = DefParser(example_def_path)
    with open(example_def_path, "r") as fp:
        assert def_parser.raw_text == fp.read()
    assert def_parser.file_name == example_def_path.name


def test_instantiation_api(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda which, molecule_slug, isotopologue_slug, dataset_name: "foo",
    )
    assert (
        DefParser(
            molecule_slug="ms", isotopologue_slug="is", dataset_name="dn"
        ).raw_text
        == "foo"
    )


def test_dataclasses_repr():
    assert repr(Isotope(42, "Foo")) == "Isotope(42Foo)"
    assert repr(Quantum("label", "format", "description")) == "Quantum(label)"
    assert repr(QuantumCase(label="foo")) == "QuantumCase(label=foo)"


def test_parse_example_def():
    def_parser = DefParser(example_def_path)
    def_parser.parse(warn_on_comments=False)

    # parsed attributes:
    assert def_parser.id == "EXOMOL.def"
    assert def_parser.iso_formula == "(40Ca)(1H)"
    assert def_parser.iso_slug == "40Ca-1H"
    assert def_parser.dataset_name == "Yadin"
    assert def_parser.version == 20160726
    assert def_parser.inchi_key.startswith("PKH")
    assert [i.element_symbol for i in def_parser.isotopes] == ["Ca", "H"]
    assert def_parser.mass == 40.970416
    assert def_parser.symmetry_group == "C"
    assert [ir.label for ir in def_parser.irreducible_representations] == [
        "Sigma+",
        "Sigma-",
    ]
    assert def_parser.max_temp == 3000.0
    assert def_parser.num_pressure_broadeners == 0
    assert def_parser.dipole_availability is False
    assert def_parser.num_cross_sections == 0
    assert def_parser.num_k_coefficients == 0
    assert def_parser.lifetime_availability is True
    assert def_parser.lande_factor_availability is False
    assert def_parser.num_states == 1892
    assert [qc.label for qc in def_parser.quanta_cases] == ["dcs"]
    assert [q.label for q in def_parser.quanta] == ["par", "v", "N", "e/f"]
    assert def_parser.num_transitions == 26980
    assert def_parser.num_trans_files == 1
    assert def_parser.max_wavenumber == 15277.72
    assert math.isnan(def_parser.high_energy_complete)

    # additional methods:
    assert def_parser.get_quanta_labels() == ["par", "v", "N", "e/f"]
    assert def_parser.number_states_columns_expected() == 9


def test_invalid_iso_formula(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text.replace(
            "(40Ca)(1H)", "(40Ham)(1Spam)"
        ),
    )
    def_parser = DefParser(isotopologue_slug="iso_slug", dataset_name="dataset")
    with pytest.raises(DefParseError, match=".*(raised in iso_slug__dataset.def).*"):
        def_parser.parse(warn_on_comments=False)


def test_invalid_num_atoms(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text.replace(
            "2                                                                       "
            "        # Number of atoms",
            "3       # Number of atoms",
        ),
    )
    def_parser = DefParser()
    with pytest.raises(DefParseError, match=".*Incorrect number of atoms in .*"):
        def_parser.parse(warn_on_comments=False)


def test_invalid_line_value_type(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text.replace("20160726", "foo"),
    )
    def_parser = DefParser()
    with pytest.raises(DefParseError, match=".*Unexpected value type*"):
        def_parser.parse(warn_on_comments=False)


def test_invalid_line_format(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text.replace("# ID", "    "),
    )
    def_parser = DefParser()
    with pytest.raises(DefParseError, match=".*Unexpected line format*"):
        def_parser.parse(warn_on_comments=False)


def test_warn_on_comments(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text,
    )
    def_parser = DefParser()
    # should not warn, as all comments are expected
    with pytest.warns(None) as record:
        def_parser.parse(warn_on_comments=True)
    assert not record
    def_parser.raw_text = def_parser.raw_text.replace("ID", "Unexpected comment")
    # now, it should warn, as one comment was changed to an unexpected str
    with pytest.warns(LineWarning):
        def_parser.parse(warn_on_comments=True)
    # should not warn though if warnings disabled
    with pytest.warns(None) as record:
        def_parser.parse(warn_on_comments=False)
    assert not record
