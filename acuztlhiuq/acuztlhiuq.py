import streamlit as st
from streamlit.web import cli as stcli
from streamlit import runtime

from googlesearch import search
import requests
from bs4 import BeautifulSoup

from langchain_ibm import WatsonxLLM
from langchain_core.prompts import PromptTemplate

from concurrent.futures import ThreadPoolExecutor

import re

import sys

st.set_page_config(initial_sidebar_state="expanded", layout="wide")

st.title("Google Latest Article Summarizer")

with st.sidebar:

    st.markdown("#### WatsonX API Key")
    st.session_state.api = st.text_input(
        "api key",
        label_visibility="collapsed",
        value="",
    )

    st.markdown("#### IBM Cloud URL")
    st.session_state.cloud_url = st.text_input(
        "url", label_visibility="collapsed", value="https://us-south.ml.cloud.ibm.com"
    )

    st.markdown("#### WatsonX.ai Project ID")
    st.session_state.project_id = st.text_input(
        "project id",
        label_visibility="collapsed",
        value="",
    )


def preprocess_text(text):
    pattern = r" +"
    # print(text)
    cleaned_text = re.sub(pattern, " ", text)
    pattern = r"\n +"
    cleaned_text = re.sub(pattern, "\n", cleaned_text)
    cleaned_text = re.sub(r"\n\n\n+", "\n\n", cleaned_text)
    return cleaned_text.strip()


def google_search(query, num_results):
    return [url for url in search(query, num_results=num_results)]


def fetch_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return response.text
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def scrape_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    paragraphs = soup.find_all("p")
    content = "\n".join([para.get_text() for para in paragraphs])
    return content


def main(query, max_num_results):
    num_results = 10
    urls = google_search(query, num_results)

    ctr = 0
    contents = []
    for idx, url in enumerate(urls):
        print(f"Scraping content from URL {idx + 1}: {url}")
        html_content = fetch_url_content(url)
        if html_content:
            content = scrape_content(html_content)
            content = preprocess_text(content)
            contents.append({"url": url, "content": content})
            print(
                f"Content from URL {idx + 1}:\n{content}\n"
            )  # Print first 1000 characters for brevity
            ctr += 1
            if ctr == max_num_results:
                break
        else:
            print(f"Failed to retrieve content from URL {idx + 1}")

    return contents


@st.cache_resource(show_spinner=False)
def get_llm(model_id, parameters):

    return WatsonxLLM(
        model_id=model_id,
        url=st.session_state.cloud_url,
        project_id=st.session_state.project_id,
        params=parameters,
        apikey=st.session_state.api,
    )


def summarize(content_dict, chain):
    print("Summarizing...")
    summary = chain.invoke({"article": content_dict["content"], "query": query})
    content_dict["summary"] = summary.strip()
    return content_dict


if st.session_state.api and st.session_state.cloud_url and st.session_state.project_id:

    query = st.text_input("Enter your google search query")

    max_num_results = st.slider("Number of top articles to be summarized", 1, 6, 3)

    if st.button("Submit") and query:

        with st.spinner(
            f'Fetching top {max_num_results} atricle{"s" if max_num_results!=1 else ""}...'
        ):
            contents = main(query, max_num_results)

        model_id = "mistralai/mixtral-8x7b-instruct-v01"

        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 1600,
            "min_new_tokens": 1,
        }

        with st.spinner("Loading LLM..."):
            watsonx_llm = get_llm(model_id, parameters)

        summary_prompt_v2 = '''Topic: """{query}"""

Article: """{article}"""

Instructions: Summarize the key points from the given article that are relevant to the specified above "Topic". The summary should be concise, coherent, \
and capture the most important information related to the above "Topic" only. Avoid including irrelevant details or information that does not directly address the above "Topic". Provide only the summary as bullet points, no additional text. 

Summary: '''

        template_2 = PromptTemplate.from_template(summary_prompt_v2)
        chain_2 = template_2 | watsonx_llm

        with st.spinner("Summarizing each article..."):
            with ThreadPoolExecutor(max_workers=6) as executor:
                summaries = executor.map(
                    summarize, contents, [chain_2 for i in range(len(contents))]
                )

        contents = list(summaries)

        prompt_for_summaries = ""
        for i in range(max_num_results):
            prompt_for_summaries = (
                f'{prompt_for_summaries}\nSummary {i}: """{{summary{i}}}"""\n'
            )

        final_prompt_template = (
            "Create a concise summary by merging the three provided summaries of different articles. Ensure the new summary closely follows the content of the original summaries without including any external information.\n"
            + prompt_for_summaries
            + "\nCombined concise summary:"
        )

        final_prompt = PromptTemplate.from_template(final_prompt_template)

        final_chain = final_prompt | watsonx_llm

        for i, content in enumerate(contents):
            with st.expander(f"Summary of article {i+1}"):
                print(content)
                st.markdown(content["summary"])
                st.markdown(f'reference: [Link to the article]({content["url"]})')

        with st.spinner("Generating final summary..."):
            invoking_param = {
                f"summary{i}": contents[i]["summary"] for i in range(max_num_results)
            }
            final_summary = final_chain.invoke(invoking_param).strip()

        with st.expander(
            f'Summary of top {max_num_results} atricle{"s" if max_num_results!=1 else ""}...',
            expanded=True,
        ):
            st.markdown(final_summary)

else:

    st.warning("Provide watsonx.ai credentials on sidebar.")

if __name__ == "__main__":
    if runtime.exists():
        print("Running ......")
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
