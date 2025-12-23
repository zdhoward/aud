import pytest

from aud.aud import Dir


@pytest.mark.xfail(reason="export_for is a placeholder by design")
def test_export_for(populated_dir):
    d = Dir(populated_dir)
    d.config_set_extensions(["wav"])
    assert d.export_for("amuse", populated_dir / "amuse")
