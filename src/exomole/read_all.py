"""
TODO: add the module documentation
"""
# TODO: write all docstrings

from pathlib import Path
import warnings

from pyvalem.formula import Formula, FormulaParseError

from .exceptions import AllParseError, AllParseWarning
from .utils import get_file_raw_text_over_api, parse_exomol_line
from .utils import DataClass


# noinspection PyUnresolvedReferences
class Molecule(DataClass):
    def __init__(self, names, formula, isotopologues):
        super().__init__(names=names, formula=formula, isotopologues=isotopologues)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.formula})"


# noinspection PyUnresolvedReferences
class Isotopologue(DataClass):
    def __init__(self, inchi_key, iso_slug, iso_formula, dataset_name, version):
        super().__init__(
            inchi_key=inchi_key,
            iso_slug=iso_slug,
            iso_formula=iso_formula,
            dataset_name=dataset_name,
            version=version,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.iso_slug})"


class AllParser:
    """
    Examples
    --------
    Instantiate the parser:
    >>> parser = AllParser(path="tests/resources/exomol_data/exomol.all")
    >>> parser.file_name
    'exomol.all'
    >>> parser.raw_text[: 13]  # first 13 characters of the text
    'EXOMOL.master'

    Parse the exomol.all text:
    >>> parser.parse(warn_on_comments=True)
    >>> parser.id
    'EXOMOL.master'
    >>> parser.version
    20210707
    >>> molecule_parsed = parser.molecules['CaH']
    >>> type(molecule_parsed)
    <class 'exomole.read_all.Molecule'>
    >>> molecule_parsed.names
    ['Calcium monohydride', 'Calcium(I) hydride']
    >>> isotopologue_parsed = molecule_parsed.isotopologues['(40Ca)(1H)']
    >>> isotopologue_parsed
    Isotopologue(40Ca-1H)
    >>> type(isotopologue_parsed)
    <class 'exomole.read_all.Isotopologue'>
    >>> isotopologue_parsed.dataset_name
    'Yadin'
    >>> isotopologue_parsed.iso_slug
    '40Ca-1H'
    """

    def __init__(self, path=None):
        self.raw_text = None
        self.file_name = None
        self._save_raw_text(path)
        # placeholders for all the attributes
        self.id = None
        self.version = None
        self.num_molecules = None
        self.num_isotopologues = None
        self.num_datasets = None
        self.molecules = None

    def _save_raw_text(self, path):
        if path is None:
            self.raw_text = get_file_raw_text_over_api("all")
            self.file_name = "exomol.all"
        else:
            with open(path, "r") as fp:
                self.raw_text = fp.read()
            self.file_name = Path(path).name

    def parse(self, warn_on_comments):
        """
        Warns
        -----
        AllParseWarning
            When?
        LineWarning
            When?
        """
        lines = self.raw_text.split("\n")
        n_orig = len(lines)

        def parse_line(expected_comment, val_type=None):
            return parse_exomol_line(
                lines,
                n_orig,
                expected_comment=expected_comment,
                file_name=self.file_name,
                val_type=val_type,
                warn_on_comments=warn_on_comments,
            )

        self.id = parse_line("ID")
        self.version = parse_line("Version number with format YYYYMMDD", int)
        self.num_molecules = parse_line("Number of molecules in the database", int)
        self.num_isotopologues = parse_line(
            "Number of isotopologues in the database", int
        )
        self.num_datasets = parse_line("Number of datasets in the database", int)
        self.molecules = {}

        # Verify the numbers of isotopologues and datasets by keeping track:
        all_isotopologues = []
        all_datasets = []
        # Also keep track of all the molecules with more than one dataset in a single
        # isotopologue:
        molecules_with_duplicate_isotopologues = []

        # loop over molecules:
        for _ in range(self.num_molecules):
            mol_names = []

            num_names = parse_line("Number of molecule names listed", int)

            # loop over the molecule names:
            for __ in range(num_names):
                mol_names.append(parse_line("Name of the molecule"))

            mol_formula = parse_line("Molecule chemical formula")
            try:
                Formula(mol_formula)
            except FormulaParseError as e:
                raise AllParseError(f"{str(e)} (raised in {self.file_name})")

            num_isotopologues = parse_line("Number of isotopologues considered", int)
            mol_isotopologues = {}

            # loop over the isotopologues:
            for __ in range(num_isotopologues):
                iso_inchi_key = parse_line("Inchi key of isotopologue")
                iso_slug = parse_line("Iso-slug")
                iso_formula = parse_line("IsoFormula")
                try:
                    Formula(iso_formula)
                except FormulaParseError as e:
                    raise AllParseError(f"{str(e)} (raised in {self.file_name})")
                iso_dataset_name = parse_line("Isotopologue dataset name")
                iso_version = parse_line("Version number with format YYYYMMDD", int)

                isotopologue = Isotopologue(
                    inchi_key=iso_inchi_key,
                    iso_slug=iso_slug,
                    iso_formula=iso_formula,
                    dataset_name=iso_dataset_name,
                    version=iso_version,
                )

                if iso_formula not in mol_isotopologues:
                    mol_isotopologues[iso_formula] = isotopologue
                else:
                    warnings.warn(
                        f"{mol_formula} lists more than one dataset for isotopologue "
                        f"{iso_formula}. Ignoring {iso_dataset_name}",
                        AllParseWarning,
                    )
                    molecules_with_duplicate_isotopologues.append(mol_formula)

                all_datasets.append(iso_dataset_name)
                all_isotopologues.append(isotopologue)

            # molecule slug is not present in the exomol.all data!
            self.molecules[mol_formula] = Molecule(
                names=mol_names, formula=mol_formula, isotopologues=mol_isotopologues
            )

        if self.num_isotopologues != len(all_isotopologues):
            warnings.warn(
                f"Number of isotopologues stated ({self.num_isotopologues}) does not "
                f"match the actual number ({len(all_isotopologues)})!",
                AllParseWarning,
            )

        if self.num_datasets != len(set(all_datasets)):
            warnings.warn(
                f"Number of datasets stated ({self.num_datasets}) does not match the "
                f"actual number ({len(set(all_datasets))})!",
                AllParseWarning,
            )
