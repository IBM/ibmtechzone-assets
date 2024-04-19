import camelot

data = camelot.read_pdf(
    '.path_to_pdf',
    pages='1',
    password=None,
    flavor='stream',
    suppress_stdout=False,
    layout_kwargs={}
)
# data[0].parsing_report
data[0].df