import streamlit as st
import os, fnmatch

def read_log_files(logFileName):
  """Reads the log/text files and returns a list of log entries."""
  log_entries = []
  with open(f"data/"+logFileName, "r") as f:
    log_entries.extend(f.readlines())
  return log_entries

def search_log_entries(query):
  """Searches for a specific string in the log entries."""
  results = []
  for entry in log_entries:
    if query in entry:
      results.append(entry)
  return results

st.title("Log Viewer, search logs/text file")
FILE_PATTERN = os.environ["file_pattern"]
fileList = [file for file in fnmatch.filter(os.listdir("data"),FILE_PATTERN)]

sel_filetered_file=st.selectbox("Select log file",options=fileList)
# Display the log entries

if sel_filetered_file:
  log_entries = read_log_files(sel_filetered_file)
  st.write("Showing contents of file: " + sel_filetered_file)
  with st.expander('Expand to view file contents', expanded=False):
    st.write(log_entries)

# Search for a specific string
query = st.text_input("Enter a search query:")
results = search_log_entries(query)
if results:
  st.write("Search results:")
  st.write(results)

