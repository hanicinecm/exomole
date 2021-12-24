from exomole.utils import DataClass


def test_():
    class DummyData(DataClass):
        def __init__(self, foo, poo):
            super().__init__(foo=foo, poo=poo)

    assert repr(DummyData(foo="foo", poo=42)) == "DummyData(foo=foo, poo=42)"
