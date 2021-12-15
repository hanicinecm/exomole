from pathlib import Path

from pyvalem.formula import Formula, FormulaParseError

from .exceptions import LineValueError, LineCommentError, DefParseError
from .utils import get_file_raw_text, parse_exomol_line
from .utils import DataClass


# noinspection PyUnresolvedReferences
class Isotope(DataClass):
    def __init__(self, number, element_symbol):
        super().__init__(number=number, element_symbol=element_symbol)

    def __repr__(self):
        return f"Isotope({self.number}{self.element_symbol})"


class IrreducibleRepresentation(DataClass):
    def __init__(self, ir_id, label, nuclear_spin_degeneracy):
        super().__init__(
            id=ir_id, label=label, nuclear_spin_degeneracy=nuclear_spin_degeneracy
        )


class QuantumCase(DataClass):
    def __init__(self, label):
        super().__init__(label=label)


# noinspection PyUnresolvedReferences
class Quantum(DataClass):
    def __init__(self, label, q_format, description):
        super().__init__(label=label, format=q_format, description=description)

    def __repr__(self):
        return f"Quantum({self.label})"


class DefParser:
    """
    Examples
    --------
    Instantiate the parser:
    >>> parser = DefParser(
    ...     path="tests/resources/exomol_data/CaH/40Ca-1H/Yadin/40Ca-1H__Yadin.def"
    ... )
    >>> parser.file_name
    '40Ca-1H__Yadin.def'
    >>> parser.raw_text[:10]  # first 10 characters of the text
    'EXOMOL.def'

    Parse the .def file:
    >>> parser.parse(warn_on_comments=True)
    >>> parser.id
    'EXOMOL.def'
    >>> parser.iso_formula
    '(40Ca)(1H)'
    >>> parser.mass
    40.970416
    >>> parser.isotopes
    [Isotope(40Ca), Isotope(1H)]
    >>> quanta = parser.quanta
    >>> quanta
    [Quantum(par), Quantum(v), Quantum(N), Quantum(e/f)]
    >>> quanta[0].description
    "total parity: '+' or '-'"
    >>> parser.lifetime_availability, parser.lande_factor_availability
    (True, False)

    Additional methods on the parsed data:
    >>> parser.get_quanta_labels()
    ['par', 'v', 'N', 'e/f']
    >>> # parser.lifetime_availability, we expect 9 columns in the .states file
    >>> parser.number_states_columns_expected()
    9
    """

    def __init__(
        self,
        path=None,
        molecule_slug=None,
        isotopologue_slug=None,
        dataset_name=None,
    ):
        self.raw_text = None
        self.file_name = None
        self._save_raw_text(path, molecule_slug, isotopologue_slug, dataset_name)
        # placeholders to all the attributes
        self.id = None
        self.iso_formula = None
        self.iso_slug = None
        self.dataset_name = None
        self.version = None
        self.inchi_key = None
        self.isotopes = None
        self.mass = None
        self.symmetry_group = None
        self.irreducible_representations = None
        self.max_temp = None
        self.num_pressure_broadeners = None
        self.dipole_availability = None
        self.num_cross_sections = None
        self.num_k_coefficients = None
        self.lifetime_availability = None
        self.lande_factor_availability = None
        self.num_states = None
        self.quanta_cases = None
        self.quanta = None
        self.num_transitions = None
        self.num_trans_files = None
        self.max_wavenumber = None
        self.high_energy_complete = None

    def _save_raw_text(self, path, molecule_slug, isotopologue_slug, dataset_name):
        """
        Save the raw text of a .def file as an instance attribute

        The .def file is either read from the local file system, or requested over the
        ExoMol public API, based on the attributes values.

        Parameters
        ----------
        path : str or Path or None
            Path leading to the .def file.
        molecule_slug : str or None
            Ignored if path is not None.
        isotopologue_slug : str or None
            Ignored if path is not None.
        dataset_name : str or None
            Ignored if path is not None.
        """
        if path is None:
            self.raw_text = get_file_raw_text(
                "def", molecule_slug, isotopologue_slug, dataset_name
            )
            self.file_name = f"{isotopologue_slug}__{dataset_name}.def"
        else:
            with open(path, "r") as fp:
                self.raw_text = fp.read()
            self.file_name = Path(path).name

    def parse(self, warn_on_comments):
        """
        Parse the .def file text from self.raw_text

        Populates all the instance attributes incrementally, util it hits the end of
        the file, or one of the exceptions is raised, signaling inconsistent .def
        file.

        Parameters
        ----------
        warn_on_comments : bool

        Raises
        -------
        DefParseError
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

        # catch all the parse_line-originated errors and wrap them in a higher-level
        # error:
        try:
            self.id = parse_line("ID")
            self.iso_formula = parse_line("IsoFormula")
            self.iso_slug = parse_line("Iso-slug")
            self.dataset_name = parse_line("Isotopologue dataset name")
            self.version = parse_line("Version number with format YYYYMMDD", int)
            self.inchi_key = parse_line("Inchi key of molecule")
            self.isotopes = []
            num_atoms = parse_line("Number of atoms", int)
            try:
                formula = Formula(self.iso_formula)
            except FormulaParseError as e:
                raise DefParseError(f"{str(e)} (raised in {self.file_name})")
            if formula.natoms != num_atoms:
                raise DefParseError(f"Incorrect number of atoms in {self.file_name}")
            for i in range(num_atoms):
                number = parse_line(f"Isotope number {i + 1}", int)
                element_symbol = parse_line(f"Element symbol {i + 1}")
                isotope = Isotope(number=number, element_symbol=element_symbol)
                self.isotopes.append(isotope)
            iso_mass_amu = float(
                parse_line("Isotopologue mass (Da) and (kg)").split()[0]
            )
            self.mass = iso_mass_amu
            self.symmetry_group = parse_line("Symmetry group")
            self.irreducible_representations = []
            num_irreducible_representations = parse_line(
                "Number of irreducible representations", int
            )
            for _ in range(num_irreducible_representations):
                ir_id = parse_line("Irreducible representation ID", int)
                label = parse_line("Irreducible representation label")
                nuclear_spin_degeneracy = parse_line("Nuclear spin degeneracy", int)
                ir = IrreducibleRepresentation(
                    ir_id=ir_id,
                    label=label,
                    nuclear_spin_degeneracy=nuclear_spin_degeneracy,
                )
                self.irreducible_representations.append(ir)
            self.max_temp = parse_line("Maximum temperature of linelist", float)
            self.num_pressure_broadeners = parse_line(
                "No. of pressure broadeners available", int
            )
            self.dipole_availability = bool(
                parse_line("Dipole availability (1=yes, 0=no)", int)
            )
            self.num_cross_sections = parse_line(
                "No. of cross section files available", int
            )
            self.num_k_coefficients = parse_line(
                "No. of k-coefficient files available", int
            )
            self.lifetime_availability = bool(
                parse_line("Lifetime availability (1=yes, 0=no)", int)
            )
            self.lande_factor_availability = bool(
                parse_line("Lande g-factor availability (1=yes, 0=no)", int)
            )
            self.num_states = parse_line("No. of states in .states file", int)
            self.quanta_cases = []
            self.quanta = []
            num_quanta_cases = parse_line("No. of quanta cases", int)
            # TODO: It is not entirely clear if num_quanta and related blocks should
            #       be nested under a quanta case, or not.
            #       If they are, I the data structures need to be changed, and the
            #       parser tweaked.
            for _ in range(num_quanta_cases):
                self.quanta_cases.append(
                    QuantumCase(label=parse_line("Quantum case label"))
                )
            num_quanta = parse_line("No. of quanta defined", int)
            for i in range(num_quanta):
                label = parse_line(f"Quantum label {i + 1}")
                q_format = parse_line(f"Format quantum label {i + 1}")
                description = parse_line(f"Description quantum label {i + 1}")
                quantum = Quantum(
                    label=label, q_format=q_format, description=description
                )
                self.quanta.append(quantum)
            self.num_transitions = parse_line("Total number of transitions", int)
            self.num_trans_files = parse_line("No. of transition files", int)
            self.max_wavenumber = parse_line("Maximum wavenumber (in cm-1)", float)
            self.high_energy_complete = parse_line(
                "Higher energy with complete set of transitions (in cm-1)", float
            )
            # TODO: This is where I stop right now, although it would be nice to finish
            #       the whole file one day.
        except (LineValueError, LineCommentError) as e:
            raise DefParseError(str(e))

    def get_quanta_labels(self):
        return [q.label for q in self.quanta]

    def number_states_columns_expected(self):
        return (
            4
            + sum([self.lifetime_availability, self.lande_factor_availability])
            + len(self.get_quanta_labels())
        )
