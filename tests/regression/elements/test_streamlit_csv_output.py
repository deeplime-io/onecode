from onecode import CsvOutput


def test_streamlit_csv_output():
    widget = CsvOutput(
        key="CsvOutput",
        value="/path/to/file.csv",
        label="My CsvOutput"
    )

    assert widget.streamlit() == """
value = os.path.relpath(value)  # allows compat with Windows
if not os.path.exists(value) and not os.path.isfile(value):
    st.warning(f'Invalid file path: {{value}}')

else:
    df = pacsv.read_csv(value).to_pandas()
    file_size = df.size // 1e6
    if file_size > 200:
        st.write(f'File too big ({file_size} Mo), data has been truncated to the first 10k rows')
        df = df[:10000]

    st.subheader(f'{label} - {os.path.basename(value)}')
    st.dataframe(df)

"""
