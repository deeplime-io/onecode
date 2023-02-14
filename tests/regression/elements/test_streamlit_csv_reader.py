from onecode import CsvReader


def test_streamlit_csv_reader():
    widget = CsvReader(
        key="CsvReader",
        value="/path/to/file.csv",
        label="My CsvReader"
    )

    assert widget.streamlit("'csv'") == """
# CsvReader csvreader
_file_csvreader = st.file_uploader(
    f'''My CsvReader''' + ': select CSV file',
    type=['csv'],
    disabled=False,
    key='csv'
)
if _file_csvreader is not None:
    csvreader = pacsv.read_csv(_file_csvreader).to_pandas()
    if _file_csvreader.size // 1e6 > 200:
        st.write(
            f'File too big ({_file_csvreader.size // 1e6} Mo)'
            ', data has been truncated to the first 10k rows'
        )
        csvreader = csvreader[:10000]
    st.dataframe(csvreader)
else:
    csvreader = None

"""
