from music_master.instruments.base import AvailabilityState, InstrumentCategory
from music_master.instruments.registry import InstrumentRegistry


def test_instrument_registry_initialization():
    registry = InstrumentRegistry()
    instruments = registry.get_all()
    assert len(instruments) > 10

    # Verify Harmonium
    harmonium = registry.get_by_id("harmonium")
    assert harmonium is not None
    assert harmonium.category == InstrumentCategory.INDIAN_CLASSICAL
    assert harmonium.availability == AvailabilityState.AVAILABLE

    # Verify Grand Piano
    piano = registry.get_by_id("grand_piano")
    assert piano is not None
    assert piano.category == InstrumentCategory.WESTERN_KEYBOARD
    assert piano.availability == AvailabilityState.AVAILABLE

    # Verify Indian instruments (Harmonium, Sitar, Tabla, Tanpura)
    sitar = registry.get_by_id("sitar")
    assert sitar is not None
    assert sitar.category == InstrumentCategory.INDIAN_CLASSICAL
    assert sitar.availability == AvailabilityState.AVAILABLE

    tabla = registry.get_by_id("tabla")
    assert tabla is not None
    assert tabla.availability == AvailabilityState.AVAILABLE

    tanpura = registry.get_by_id("tanpura")
    assert tanpura is not None
    assert tanpura.availability == AvailabilityState.AVAILABLE

    # Verify synthesized instruments (e.g. Bansuri is now AVAILABLE)
    bansuri = registry.get_by_id("bansuri")
    assert bansuri is not None
    assert bansuri.availability == AvailabilityState.AVAILABLE

    # Verify Planned instruments (e.g. Veena)
    veena = registry.get_by_id("veena")
    assert veena is not None
    assert veena.availability == AvailabilityState.PLANNED
