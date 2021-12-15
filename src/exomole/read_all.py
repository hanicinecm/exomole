from pathlib import Path

from .utils import get_file_raw_text
from .utils import DataClass


class Molecule(DataClass):
    def __init__(self, names, formula, isotopologues):
        super().__init__(names=names, formula=formula, isotopologues=isotopologues)


class Isotopologue(DataClass):
    def __init__(self, inchi_key, iso_slug, iso_formula, dataset_name, version):
        super().__init__(
            inchi_key=inchi_key,
            iso_slug=iso_slug,
            iso_formula=iso_formula,
            dataset_name=dataset_name,
            version=version,
        )


class AllParser:
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
            self.raw_text = get_file_raw_text("all")
            self.file_name = "exomol.all"
        else:
            with open(path, "r") as fp:
                self.raw_text = fp.read()
            self.file_name = Path(path).name

    def parse(self):
        raise NotImplementedError
