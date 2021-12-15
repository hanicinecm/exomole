import requests

from .utils import get_file_raw_text


class Isotope:
    def __init__(self, number, element_symbol):
        self.number = number
        self.element_symbol = element_symbol

    def __repr__(self):
        return f"Isotope({self.number}{self.element_symbol})"


class IrreducibleRepresentation:
    def __init__(self, ir_id, label, nuclear_spin_degeneracy):
        self.id = ir_id
        self.label = label
        self.nuclear_spin_degeneracy = nuclear_spin_degeneracy

    def __repr__(self):
        return (
            f"IrreducibleRepresentation("
            f"{self.id}, {self.label}, {self.nuclear_spin_degeneracy})"
        )


class QuantumCase:
    def __init__(self, label):
        self.label = label

    def __repr__(self):
        return f"QuantumCase({self.label})"


class Quantum:
    def __init__(self, label, q_format, description):
        self.label = label
        self.format = q_format
        self.description = description

    def __repr__(self):
        return f"Quantum({self.label}, {self.format}, {self.description})"


class DefParser:
    def __init__(
        self,
        path=None,
        molecule_slug=None,
        isotopologue_slug=None,
        dataset_name=None,
        warn_on_comments=False,
    ):
        self.raw_text = None
        self._save_raw_text(path, molecule_slug, isotopologue_slug, dataset_name)
        # placeholders to all the attributes
        self.id = None
        self.iso_formula = None
        self.iso_slug = None
        self.dataset_name = None
        self.inchi_key = None
        self.isotopes = None
        self.mass = None
        self.symmetry_group = None
        self.irreducible_representations = None
        self.mas_temp = None
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
        """Save the raw text of a .def file as an instance attribute

        The .def file is either read from the local file system, or requested over the
        ExoMol public API, based on the attributes values.

        Parameters
        ----------
        path : str | Path
            Path leading to the .def file.
        molecule_slug : str
            Ignored if path is not None.
        isotopologue_slug : str
            Ignored if path is not None.
        dataset_name : str
            Ignored if path is not None.
        """
        if path is None:
            raw_text = get_file_raw_text(
                "def", molecule_slug, isotopologue_slug, dataset_name
            )
        else:
            with open(path, "r") as fp:
                raw_text = fp.read()
        self.raw_text = raw_text

    def parse(self, warn_on_comments):
        lines = self.raw_text.split("\n")
        n_orig = len(lines)

        def parse_line(expected_comment, val_type=None):
            return parse_exomol_line(
                lines,
                n_orig,
                expected_comment=expected_comment,
                file_name=file_name,
                val_type=val_type,
                raise_warnings=raise_warnings,
            )

        # catch all the parse_line-originated errors and wrap them in a higher-level
        # error:
        try:
            kwargs = {
                "raw_text": exomol_def_raw,
                "id": parse_line("ID"),
                "iso_formula": parse_line("IsoFormula"),
                "iso_slug": parse_line("Iso-slug"),
                "dataset_name": parse_line("Isotopologue dataset name"),
                "version": parse_line("Version number with format YYYYMMDD", int),
                "inchi_key": parse_line("Inchi key of molecule"),
                "isotopes": [],
            }
            num_atoms = parse_line("Number of atoms", int)
            try:
                formula = Formula(kwargs["iso_formula"])
            except FormulaParseError as e:
                raise DefParseError(f"{str(e)} (raised in {file_name})")
            if formula.natoms != num_atoms:
                ds_name = f'{kwargs["iso_slug"]}__{kwargs["dataset_name"]}.def'
                raise DefParseError(f"Incorrect number of atoms in {ds_name}")
            for i in range(num_atoms):
                isotope_kwargs = {
                    "number": parse_line(f"Isotope number {i + 1}", int),
                    "element_symbol": parse_line(f"Element symbol {i + 1}"),
                }
                isotope = Isotope(**isotope_kwargs)
                kwargs["isotopes"].append(isotope)
            iso_mass_amu = float(
                parse_line("Isotopologue mass (Da) and (kg)").split()[0]
            )
            kwargs.update(
                {
                    "mass": iso_mass_amu,
                    "symmetry_group": parse_line("Symmetry group"),
                    "irreducible_representations": [],
                }
            )
            num_irreducible_representations = int(
                parse_line("Number of irreducible representations")
            )
            for _ in range(num_irreducible_representations):
                ir_kwargs = {
                    "id": parse_line("Irreducible representation ID", int),
                    "label": parse_line("Irreducible representation label"),
                    "nuclear_spin_degeneracy": parse_line(
                        "Nuclear spin degeneracy", int
                    ),
                }
                ir = IrreducibleRepresentation(**ir_kwargs)
                kwargs["irreducible_representations"].append(ir)
            kwargs.update(
                {
                    "max_temp": parse_line("Maximum temperature of linelist", float),
                    "num_pressure_broadeners": parse_line(
                        "No. of pressure broadeners available", int
                    ),
                    "dipole_availability": bool(
                        parse_line("Dipole availability (1=yes, 0=no)", int)
                    ),
                    "num_cross_sections": parse_line(
                        "No. of cross section files available", int
                    ),
                    "num_k_coefficients": parse_line(
                        "No. of k-coefficient files available", int
                    ),
                    "lifetime_availability": bool(
                        parse_line("Lifetime availability (1=yes, 0=no)", int)
                    ),
                    "lande_factor_availability": bool(
                        parse_line("Lande g-factor availability (1=yes, 0=no)", int)
                    ),
                    "num_states": parse_line("No. of states in .states file", int),
                    "quanta_cases": [],
                    "quanta": [],
                }
            )
            num_quanta_cases = parse_line("No. of quanta cases", int)
            # TODO: it is not entirely clear if num_quanta and related blocks are nested
            #       under a quanta case, or not. If they are, I need to change the data
            #       structures, and rewrite the parser a bit.
            for _ in range(num_quanta_cases):
                kwargs["quanta_cases"].append(
                    QuantumCase(label=parse_line("Quantum case label"))
                )
            num_quanta = parse_line("No. of quanta defined", int)
            for i in range(num_quanta):
                q_kwargs = {
                    "label": parse_line(f"Quantum label {i + 1}"),
                    "format": parse_line(f"Format quantum label {i + 1}"),
                    "description": parse_line(f"Description quantum label {i + 1}"),
                }
                quantum = Quantum(**q_kwargs)
                kwargs["quanta"].append(quantum)
            kwargs.update(
                {
                    "num_transitions": parse_line("Total number of transitions"),
                    "num_trans_files": parse_line("No. of transition files"),
                    "max_wavenumber": parse_line("Maximum wavenumber (in cm-1)"),
                    "high_energy_complete": parse_line(
                        "Higher energy with complete set of transitions (in cm-1)"
                    ),
                }
            )

            return ExomolDef(**kwargs)
        except (LineValueError, LineCommentError) as e:
            raise DefParseError(str(e))
