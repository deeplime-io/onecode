from onecode import Dropdown, Keyword


def test_streamlit_dropdown_single_fixed_options():
    widget = Dropdown(
        key="Dropdown",
        value="A",
        label="My Dropdown",
        multiple=False,
        options=["A", "B", "C"]
    )

    assert widget.streamlit("'dd'") == """
try:
    _options_dropdown = ['A', 'B', 'C']
except:
    _options_dropdown = []

if False: # is dropdown multiple?
    _default_dropdown = [v for v in '''A''' if v in _options_dropdown]
else:
    _default_dropdown = pydash.find_index(_options_dropdown, lambda x: x == '''A''')
    _default_dropdown = _default_dropdown if _default_dropdown >= 0 else 0

# Dropdown dropdown
dropdown = st.selectbox(
    '''My Dropdown''',
    index=_default_dropdown,
    options=_options_dropdown,
    disabled=False,
    key='dd'
)

"""


def test_streamlit_dropdown_multiple_fixed_options():
    widget = Dropdown(
        key="Dropdown",
        value=["A", "B"],
        label="My Dropdown",
        multiple=True,
        options=["A", "B", "C"]
    )

    assert widget.streamlit("'dd'") == """
try:
    _options_dropdown = ['A', 'B', 'C']
except:
    _options_dropdown = []

if True: # is dropdown multiple?
    _default_dropdown = [v for v in ['A', 'B'] if v in _options_dropdown]
else:
    _default_dropdown = pydash.find_index(_options_dropdown, lambda x: x == ['A', 'B'])
    _default_dropdown = _default_dropdown if _default_dropdown >= 0 else 0

# Dropdown dropdown
dropdown = st.multiselect(
    '''My Dropdown''',
    default=_default_dropdown,
    options=_options_dropdown,
    disabled=False,
    key='dd'
)

"""


def test_streamlit_dropdown_single_dynamic_options():
    widget = Dropdown(
        key="Dropdown",
        value="A",
        label="My Dropdown",
        multiple=False,
        options="$x$"
    )

    assert widget.streamlit("'dd'") == f"""
try:
    _options_dropdown = {Keyword.DATA}["x"]
except:
    _options_dropdown = []

if False: # is dropdown multiple?
    _default_dropdown = [v for v in '''A''' if v in _options_dropdown]
else:
    _default_dropdown = pydash.find_index(_options_dropdown, lambda x: x == '''A''')
    _default_dropdown = _default_dropdown if _default_dropdown >= 0 else 0

# Dropdown dropdown
dropdown = st.selectbox(
    '''My Dropdown''',
    index=_default_dropdown,
    options=_options_dropdown,
    disabled=False,
    key='dd'
)

"""


def test_streamlit_dropdown_multiple_dynamic_options():
    widget = Dropdown(
        key="Dropdown",
        value=["A", "B"],
        label="My Dropdown",
        multiple=True,
        options="$x$"
    )

    assert widget.streamlit("'dd'") == f"""
try:
    _options_dropdown = {Keyword.DATA}["x"]
except:
    _options_dropdown = []

if True: # is dropdown multiple?
    _default_dropdown = [v for v in ['A', 'B'] if v in _options_dropdown]
else:
    _default_dropdown = pydash.find_index(_options_dropdown, lambda x: x == ['A', 'B'])
    _default_dropdown = _default_dropdown if _default_dropdown >= 0 else 0

# Dropdown dropdown
dropdown = st.multiselect(
    '''My Dropdown''',
    default=_default_dropdown,
    options=_options_dropdown,
    disabled=False,
    key='dd'
)

"""
