from onecode import Mode, Project, SectionHeader


def test_console_section_header():
    Project().mode = Mode.CONSOLE

    widget = SectionHeader(
        key="SectionHeader",
        value="My SectionHeader",
        metadata="data"
    )

    assert type(widget()) == SectionHeader
    assert widget.metadata == "data"
    assert widget.kind == "SectionHeader"


def test_execute_section_header():
    Project().mode = Mode.EXECUTE

    widget = SectionHeader(
        key="SectionHeader",
        value="My SectionHeader"
    )

    assert widget() == "My SectionHeader"
    assert widget.key == "sectionheader"


def test_extract_all_section_header():
    Project().mode = Mode.EXTRACT_ALL

    widget = SectionHeader(
        key="SectionHeader",
        value="My SectionHeader"
    )

    assert widget() == ('sectionheader', {
        "key": "sectionheader",
        "kind": "SectionHeader",
        "label": "SectionHeader",
        "value": "My SectionHeader",
        "count": None,
        "disabled": "False",
        "optional": False
    })


def test_extract_all_section_header_with_data():
    Project().mode = Mode.EXTRACT_ALL
    Project().data = {
        "sectionheader": "OneCode rocks!"
    }

    widget = SectionHeader(
        key="SectionHeader",
        value="My SectionHeader"
    )

    assert widget() == ('sectionheader', {
        "key": "sectionheader",
        "kind": "SectionHeader",
        "label": "SectionHeader",
        "value": "OneCode rocks!",
        "count": None,
        "disabled": "False",
        "optional": False
    })


def test_load_then_execute_section_header():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "sectionheader": "OneCode rocks!"
    }

    widget = SectionHeader(
        key="SectionHeader",
        value="My SectionHeader"
    )

    assert widget() == "OneCode rocks!"
    assert widget.key == "sectionheader"
    assert widget.label == "'''SectionHeader'''"
    assert widget._label == "SectionHeader"


def test_load_then_execute_section_header_no_key():
    Project().mode = Mode.LOAD_THEN_EXECUTE
    Project().data = {
        "no_sectionheader": "OneCode rocks!"
    }

    widget = SectionHeader(
        key="SectionHeader",
        value="My SectionHeader"
    )

    assert widget() == "My SectionHeader"
    assert widget.key == "sectionheader"
    assert widget.label == "'''SectionHeader'''"
    assert widget._label == "SectionHeader"
