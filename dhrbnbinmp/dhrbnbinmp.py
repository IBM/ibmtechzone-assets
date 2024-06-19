import streamlit as st
from streamlit.web import cli as stcli
from streamlit import runtime

from ibm_watsonx_ai import APIClient
from ibm_watson_machine_learning.foundation_models import Model

from concurrent.futures import ThreadPoolExecutor


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.header("WatsonX LLM Arena")


def initilize_session_state(value):
    if value not in st.session_state:
        st.session_state[value] = False


def get_ga_llms_list(api_key, cloud_url, project_id):
    wml_credentials = {
        "apikey": api_key,
        "url": cloud_url,
    }

    # Create an instance of the APIClient
    client = APIClient(wml_credentials)
    client.set.default_project(project_id)

    llms_info = client.foundation_models.TextModels

    llm_ids = [model.value for model in llms_info]

    return llm_ids


def print_on_columns(lst):

    rows = (len(lst) // 2) if (len(lst) % 2) == 0 else (len(lst) // 2) + 1
    cols = [st.columns(2) for i in range(rows)]
    item_no = 0
    for row in range(rows):
        for col in cols[row]:
            with col.container(height=300, border=True):
                st.caption(lst[item_no][0])
                # with col.expander(lst[item_no][0], expanded=True):
                st.markdown(lst[item_no][1])
            item_no += 1


@st.cache_resource
def load_llm(model_id, params, api, url, project_id):
    print(f"Loading {model_id}")
    model = Model(
        model_id=model_id,
        params=params,
        credentials={
            "url": url,
            "apikey": api,
        },
        project_id=project_id,
    )
    return (model_id, model)


def get_llm_response(model_id, model, prompt):

    response = model.generate_text(prompt)

    return (model_id, response)


with st.sidebar:

    st.markdown("#### WatsonX API Key")
    st.session_state.api = st.text_input(
        "api key",
        label_visibility="collapsed",
        value="8lzuqCQlXFLDuQSKoMxocfgpHIQIbLU4YxWiislYPmjM",
    )

    st.markdown("#### IBM Cloud URL")
    st.session_state.cloud_url = st.text_input(
        "url", label_visibility="collapsed", value="https://us-south.ml.cloud.ibm.com"
    )

    st.markdown("#### WatsonX.ai Project ID")
    st.session_state.project_id = st.text_input(
        "project id",
        label_visibility="collapsed",
        value="7629055d-8e95-4c3a-9ca4-de781b2a165b",
    )


if st.session_state.api and st.session_state.cloud_url and st.session_state.project_id:
    print(st.session_state.api, st.session_state.cloud_url, st.session_state.project_id)

    initilize_session_state("llm_list")

    if not st.session_state.llm_list:
        st.session_state.llm_list = get_ga_llms_list(
            st.session_state.api,
            st.session_state.cloud_url,
            st.session_state.project_id,
        )
    initilize_session_state("selected_models")
    st.markdown("Select LLM Models")
    selected_models = st.multiselect(
        "LLM Selection",
        options=st.session_state.llm_list,
        label_visibility="collapsed",
        max_selections=6,
    )

    decoding_method = st.selectbox(
        "Select decoding Method",
        options=["Sample", "Greedy"],
        key="decoding_method",
    )
    with st.expander("LLM Parameters"):
        if st.session_state.decoding_method == "Greedy":
            slider, min = st.columns([1, 1])

            with slider:
                repeatition_penalty = st.slider(
                    "Repetition Penalty",
                    key="repeatition_penalty",
                    min_value=1.0,
                    max_value=2.0,
                    step=0.05,
                    value=1.0,
                )

            with slider:
                raw_stop_sequences = st.text_input(
                    r"Provide stop sequences",
                    help='Max 6, comma separated and enclosed in double quotes\nExample: "\\n", "\\n\\n"',
                )
                stop_sequences = [
                    i.strip().strip('"') for i in raw_stop_sequences.split(",")
                ]
                initilize_session_state("stop_sequences")
                st.session_state.stop_sequences = stop_sequences
            with min:
                min_tokens = st.number_input("Min tokens", key="min_tokens", value=1)
                max_tokens = st.number_input("Max tokens", key="max_tokens", value=200)

            llm_params = {
                "decoding_method": "greedy",
                "max_new_tokens": max_tokens,
                "min_new_tokens": min_tokens,
                "repetition_penalty": repeatition_penalty,
                "stop_sequesnces": stop_sequences,
            }

        elif decoding_method == "Sample":

            slider, max = st.columns([1, 1])
            with slider:
                repeatition_penalty = st.slider(
                    "Repetition Penalty",
                    min_value=1.0,
                    max_value=2.0,
                    step=0.05,
                    value=1.0,
                )
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=2.0,
                    step=0.01,
                    value=0.0,
                )
                top_p = st.slider(
                    "Top P", min_value=0.0, max_value=1.0, step=0.01, value=1.0
                )
                top_k = st.slider("Top k", min_value=1, max_value=100, value=50)
            with max:
                random_seed = st.number_input("Random Seed", value=42)
                raw_stop_sequences = st.text_input(
                    r"Provide stop sequences",
                    help='Max 6, comma separated and enclosed in double quotes\nExample: "\\n", "\\n\\n"',
                )
                stop_sequences = [
                    i.strip().strip('"') for i in raw_stop_sequences.split(",")
                ]
                min_tokens = st.number_input("Min tokens", value=1)
                max_tokens = st.number_input("Max tokens", value=200)
            llm_params = {
                "decoding_method": "sample",
                "max_new_tokens": max_tokens,
                "min_new_tokens": min_tokens,
                "temperature": temperature,
                "random_seed": random_seed,
                "repetition_penalty": repeatition_penalty,
                "top_k": top_k,
                "top_p": top_p,
            }

    st.session_state["llm_params"] = llm_params

    initilize_session_state("loaded_llms")

    st.markdown("#### Enter your prompt")
    prompt = st.text_area(
        "Prompt", label_visibility="collapsed", key="prompt", height=300
    )
    print("selected models", selected_models)
    print("session state", st.session_state.selected_models)
    if selected_models and prompt.strip() and st.button("Submit"):
        if not st.session_state.selected_models:
            st.session_state.selected_models = []
        print(sorted(selected_models), sorted(st.session_state.selected_models))
        if sorted(selected_models) != sorted(st.session_state.selected_models):
            print("Loading Models")
            st.session_state.selected_models = selected_models

            with st.spinner("Loading above selected models..."):
                params = [st.session_state["llm_params"]] * len(
                    st.session_state.selected_models
                )
                with ThreadPoolExecutor(max_workers=6) as executor:
                    loaded_models = executor.map(
                        load_llm,
                        st.session_state.selected_models,
                        params,
                        [st.session_state.api for i in params],
                        [st.session_state.cloud_url for i in params],
                        [st.session_state.project_id for i in params],
                    )
                loaded_models = list(loaded_models)
                st.session_state.loaded_llms = loaded_models
        args = [(i[0], i[1], prompt) for i in st.session_state.loaded_llms]
        with st.spinner("Getting LLM responses..."):
            with ThreadPoolExecutor(max_workers=6) as executor:
                # Use zip to ensure the parameters are correctly mapped
                responses = executor.map(lambda params: get_llm_response(*params), args)
        responses = list(responses)
        responses.sort(key=lambda a: a[0])
        print("final responses", responses)
        print_on_columns(responses)

else:
    st.warning("Please provide the WatsonX credentials")
    
if __name__ == '__main__':
    if runtime.exists():
        print("Running ......")
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
