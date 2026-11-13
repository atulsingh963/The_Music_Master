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

    # Verify Planned instruments
    sitar = registry.get_by_id("sitar")
    assert sitar is not None
    assert sitar.availability == AvailabilityState.PLANNED
