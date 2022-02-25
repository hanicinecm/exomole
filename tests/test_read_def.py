import math

import pytest

import exomole
from exomole.exceptions import DefParseError, LineWarning
from exomole.read_def import (
    DefParser,
    Isotope,
    QuantumCase,
    Quantum,
    DefConsistencyError,
    parse_def,
)
from . import resources_path

example_def_path = resources_path.joinpath(
    "exomol_data", "CaH", "40Ca-1H", "Yadin", "40Ca-1H__Yadin.def"
)

with open(example_def_path, "r") as fp:
    example_def_raw_text = fp.read()


def test_instantiation_path():
    def_parser = DefParser(example_def_path)
    assert def_parser.raw_text == example_def_raw_text
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
    assert def_parser.get_states_header() == (
        ["i", "E", "g_tot", "J", "tau", "par", "v", "N", "e/f"]
    )


@pytest.mark.parametrize(
    "lifetime_availability, lande_factor_availability, header_part",
    (
        (True, True, ["tau", "g_J"]),
        (True, False, ["tau"]),
        (False, True, ["g_J"]),
        (False, False, []),
    ),
)
def test_states_header(
    monkeypatch, lifetime_availability, lande_factor_availability, header_part
):
    def_parser = DefParser(example_def_path)
    q_labels = ["foo", "poo"]
    monkeypatch.setattr(def_parser, "get_quanta_labels", lambda: q_labels)
    monkeypatch.setattr(def_parser, "lifetime_availability", lifetime_availability)
    monkeypatch.setattr(
        def_parser, "lande_factor_availability", lande_factor_availability
    )
    assert (
        def_parser.get_states_header()
        == ["i", "E", "g_tot", "J"] + header_part + q_labels
    )


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


def test_invalid_isotope_formula(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text.replace(
            "Ca  # Element symbol 1", "Carrot  # Element symbol 1"
        ),
    )
    with pytest.raises(DefParseError):
        DefParser().parse(warn_on_comments=False)


def test_invalid_num_atoms(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text.replace(
            "2  # Number of atoms",
            "3  # Number of atoms",
        ),
    )
    def_parser = DefParser()
    with pytest.raises(DefParseError, match=".*Incorrect number of atoms in .*"):
        def_parser.parse(warn_on_comments=False)


def test_incorrect_mass(monkeypatch):
    incorrect_mass = 42.0
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text.replace(
            "40.970416 6.80329753e-26  # Isotopologue mass (Da) and (kg)",
            f"{incorrect_mass} 6.80329753e-26  # Isotopologue mass (Da) and (kg)",
        ),
    )
    def_parser = DefParser()
    with pytest.warns(LineWarning, match="Incorrect isotopologue mass.*"):
        def_parser.parse(warn_on_comments=False)
    assert def_parser.mass != incorrect_mass  # was the mass corrected?


def test_invalid_line_value_type(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text.replace("20160726", "foo"),
    )
    def_parser = DefParser()
    with pytest.raises(DefParseError, match=".*Unexpected value type.*"):
        def_parser.parse(warn_on_comments=False)


def test_invalid_line_format(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text.replace("# ID", "    "),
    )
    def_parser = DefParser()
    with pytest.raises(DefParseError, match=".*Unexpected line format.*"):
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


def test_unexpected_file_id(monkeypatch):
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: example_def_raw_text.replace(
            "EXOMOL.def", "EXOMOL.spam"
        ),
    )
    def_parser = DefParser()
    with pytest.raises(DefParseError, match=".*Unexpected ID.*"):
        def_parser.parse(warn_on_comments=False)


def test_inconsistent_number_of_isotopes(monkeypatch):
    # add one duplicate isotope into the number of atoms and the formula, but not
    # as the actual isotope lines. This is what is common in .def files and should
    # parse with warning.
    patched_text = example_def_raw_text.replace(
        "(40Ca)(1H)  # IsoFormula", "(40Ca)(1H)2  # IsoFormula"
    ).replace("2  # Number of atoms", "3  # Number of atoms")
    # but still only 40Ca and 1H isotopes listed
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: patched_text,
    )
    def_parser = DefParser()
    with pytest.warns(LineWarning, match="Incorrect number of isotopes listed.*"):
        def_parser.parse(warn_on_comments=False)
    assert len(def_parser.isotopes) == 2


def test_duplicated_isotopes(monkeypatch):
    patched_text = (
        example_def_raw_text.replace(
            "(40Ca)(1H)  # IsoFormula", "(40Ca)(1H)2  # IsoFormula"
        )
        .replace("2  # Number of atoms", "3  # Number of atoms")
        .replace(
            "40.970416 6.80329753e-26  # Isotopologue mass (Da) and (kg)",
            "1  # Isotope number 3\n"
            "H  # Element symbol 3\n"
            "41.978240 6.80329753e-26  # Isotopologue mass (Da) and (kg)",
        )
    )
    monkeypatch.setattr(
        exomole.read_def,
        "get_file_raw_text_over_api",
        lambda *args, **kwargs: patched_text,
    )
    def_parser = DefParser()
    with pytest.warns(None) as record:
        def_parser.parse(warn_on_comments=True)
    assert not record
    assert len(def_parser.isotopes) == 3


def test_check_consistency_over_api(monkeypatch):
    monkeypatch.setattr(DefParser, "_save_raw_text", lambda *args, **kwargs: None)
    def_parser = DefParser(molecule_slug="", isotopologue_slug="", dataset_name="")
    with pytest.raises(AssertionError):
        def_parser.check_consistency()


def test_check_consistency(monkeypatch):
    def_parser = DefParser(
        path=resources_path.joinpath(
            "exomol_data",
            "CaH",
            "40Ca-1H_states-and-trans",
            "Yadin",
            "40Ca-1H__Yadin.def",
        )
    )
    def_parser.parse(warn_on_comments=False)
    assert len(def_parser.get_states_header()) == 9

    monkeypatch.setattr(exomole.read_def, "get_num_columns", lambda x: 10)
    with pytest.raises(DefConsistencyError, match=".* number of columns .*"):
        def_parser.check_consistency()

    monkeypatch.setattr(exomole.read_def, "get_num_columns", lambda x: 9)
    def_parser.check_consistency()

    def_parser = DefParser(
        path=resources_path.joinpath(
            "exomol_data", "CaH", "40Ca-1H_only-def", "Yadin", "40Ca-1H__Yadin.def"
        )
    )
    def_parser.parse(warn_on_comments=False)
    with pytest.raises(DefConsistencyError, match=".* file needs to exist .*"):
        def_parser.check_consistency()

    def_parser = DefParser(
        path=resources_path.joinpath(
            "exomol_data", "CaH", "40Ca-1H_no-trans", "Yadin", "40Ca-1H__Yadin.def"
        )
    )
    def_parser.parse(warn_on_comments=False)
    with pytest.raises(DefConsistencyError, match="No trans files found .*"):
        def_parser.check_consistency()

    # and without parsing:
    def_parser = DefParser(
        path=resources_path.joinpath(
            "exomol_data",
            "CaH",
            "40Ca-1H_states-and-trans",
            "Yadin",
            "40Ca-1H__Yadin.def",
        )
    )
    def_parser.check_consistency()


def test_parse_def_all_good(monkeypatch):
    parser = parse_def(
        isotopologue_slug="40Ca-1H", data_dir_path=resources_path / "exomol_data"
    )
    assert parser.parsed is True

    monkeypatch.setattr(DefParser, "parse", lambda *args, **kwargs: None)
    parser = parse_def(
        isotopologue_slug="24Mg-1H",
        dataset_name="Yadin",
        data_dir_path=resources_path / "exomol_data",
    )
    assert parser.parsed is False  # the .parse was monkey-patched so the flag remains


def test_parse_def_failing():
    with pytest.raises(DefParseError, match="No .def file .*"):
        parse_def(
            isotopologue_slug="40Ca-1H_empty-dir",
            data_dir_path=resources_path / "exomol_data",
        )

    with pytest.raises(DefParseError, match="Multiple .def files .*"):
        parse_def(
            isotopologue_slug="24Mg-1H",
            data_dir_path=resources_path / "exomol_data",
        )
