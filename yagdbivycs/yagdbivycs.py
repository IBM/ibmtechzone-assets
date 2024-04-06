
import streamlit as st
from datetime import datetime
import pandas as pd


# Load the CSV file
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    return data


def main():

    st.set_page_config(
        page_icon=":robot:",
        layout="wide",
        initial_sidebar_state="expanded"
    )


    st.image('logo_small.png')
    st.title("Market Insights")


    col_main, col_asist = st.columns([1.5,0.5])


    with col_main:
        st.write("\n\n\n")
        st.write("\n\n\n")
        st.write("Good Morning, Traders!")

        # Create a sidebar navigation
        st.sidebar.title("Choose A Date")
        page = st.sidebar.radio("Go to", ("Today's News: 2024-01-16", "Previous Day's News: 2024-01-15", "Quantitative View"))

        # Page 1 content
        if page == "Today's News: 2024-01-16":
            home_page()

        # Page 2 content
        elif page == "Previous Day's News: 2024-01-15":
            second_page()

        elif page == 'Quantitative View':
            third_page()

    with col_asist:
        # Load and display the contents of components.html
        with open("components.html", "r") as f:
            components_html = f.read()
        st.components.v1.html(components_html, width=350, height=700, scrolling=True)




def home_page():
        tab1, tab2, tab3, tab4 = st.tabs(["Top News", "Corporate Action News", "Other News", "All News"])

        with tab1:
            top_news_main('relevancy_actionable_v4.csv')


        with tab2:
            cor_news_main('relevancy_actionable_v4.csv')


        with tab3:
            other_news_main('relevancy_actionable_v4.csv')


        with tab4:
            all_news_main('relevancy_actionable_v4.csv')







def second_page():

        tab1, tab2, tab3, tab4 = st.tabs(["Top News", "Corporate Action News", "Other News", "All News"])

        with tab1:
            top_news_main('relevancy_actionable_jan15.csv')


        with tab2:
            cor_news_main('relevancy_actionable_jan15.csv')


        with tab3:
            other_news_main('relevancy_actionable_jan15.csv')


        with tab4:
            all_news_main('relevancy_actionable_jan15.csv')

def  third_page():
    tab1, tab2 = st.tabs(["Aggregated", "Individual"])

    with tab2:
        quant = load_data('quant.csv')
        def make_words(key_list):
            try:
                return ", ".join(eval(key_list))
            except Exception as e:
                return None
        quant['Keywords'] = quant.apply(lambda row: make_words(row['Keywords']), axis = 1)
        quant['Action Keywords'] = quant.apply(lambda row: make_words(row['Action Keywords']), axis = 1)

        # st.dataframe(quant, use_container_width=True)
        st.dataframe(quant, use_container_width=True,
                    column_config={
                        "Keywords": st.column_config.ListColumn(),
                        "Action Keywords": st.column_config.ListColumn(),
                        "Link": st.column_config.LinkColumn()
                    }, hide_index=True)

    with tab1:
        quant = load_data('quant.csv')
        agg = load_data('aggregate.csv')
        agg.insert(0, "Select", False)
        def make_words(key_list):
            try:
                return ", ".join(eval(key_list))
            except Exception as e:
                return None
        agg['Keywords'] = agg['Keywords'].apply(make_words)
        agg['Action Keywords'] = agg['Action Keywords'].apply(make_words)
        quant['Keywords'] = quant['Keywords'].apply(make_words)
        quant['Action Keywords'] = quant['Action Keywords'].apply(make_words)
        
        st.write('Select one or multiple tickers to view an expanded table that shows impact levels, sentiment scores, article titles, and respective article links for each article related to that ticker.')
        
        edited_df = st.data_editor(agg, use_container_width=True,
                    column_config={
                        "Keywords": st.column_config.ListColumn(),
                        "Action Keywords": st.column_config.ListColumn(),
                        "Select": st.column_config.CheckboxColumn(),
                        "Link": st.column_config.LinkColumn()
                    }, hide_index=True)

        if edited_df.Select.any():
            st.write("*Expanded View*")

            subset = edited_df[edited_df.Select]

            indices = []
            for ticker in subset['Ticker'].tolist():
                for index, row in quant.iterrows():
                    if row['Ticker'] == ticker:
                        indices.append(index)

            st.dataframe(quant.iloc[indices].reset_index(drop=True),hide_index=True,use_container_width=True,
                         column_config={
                            "Keywords": st.column_config.ListColumn(),
                            "Action Keywords": st.column_config.ListColumn(),
                            "Link": st.column_config.LinkColumn()
                        })






def top_news_main(file):

    data = load_data(file)
    #RELEVANCY RANKING
    try:
        most = data.groupby('Impact_Level').get_group('Most Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        most = pd.DataFrame()
    try:
        high = data.groupby('Impact_Level').get_group('High Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        high = pd.DataFrame()
    try:
        moderate = data.groupby('Impact_Level').get_group('Moderate Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        moderate = pd.DataFrame()
    try:
        low = data.groupby('Impact_Level').get_group('Low Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        low = pd.DataFrame()
    try:
        least = data.groupby('Impact_Level').get_group('Least Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        least = pd.DataFrame()
    frames = [most, high, moderate, low, least]
    result = pd.concat(frames).reset_index(drop=True)


    news = pd.DataFrame()
    relevant = pd.DataFrame()
    search_query = st.text_input("Filter/Search", key="0")

    rel_indices = []
    for index, row in result.iterrows():
        if row['is_Relevant'] == 'Relevant':
            rel_indices.append(index)

        relevant = result.iloc[rel_indices].reset_index(drop=True)

    indices = []
    if search_query:
        for index, row in relevant.iterrows():
            if search_query.lower() in row['summary'].lower() or search_query.lower() in row['Title'].lower():
                indices.append(index)

        news = relevant.iloc[indices]
    else:
        news = relevant



    for index, row in news.iterrows():
        summary_lines = row['summary'].split('\n')
        text = st.subheader(f":blue[{row['Title']}]")

        #IF THERE IS RELEVANT securities lending data, all of it will show
        #else just the ticker will show
        if len(eval(row['CUSIP'])) > 0:

            st.caption(f"**Tickers:** {', '.join(eval(row['Tickers']))} **CUSIP:** {', '.join(eval(row['CUSIP']))} **Utilization:** {', '.join([str(i) for i in eval(row['Utilization'])])} **1D Fee:** {', '.join([str(i) for i in eval(row['1_Day_Fee'])])} **10D Fee:** {', '.join([str(i) for i in eval(row['10_Day_Fee'])])}")
        else:
            st.caption(f"**Tickers:** {', '.join(eval(row['Tickers']))}")

        st.write('\n'.join(summary_lines).replace('$', '\$'))

        if isinstance(row['Other_keywords_present'],str):
            st.caption(f"**{' | '.join(eval(row['Other_keywords_present']))}**")
        st.divider()


def cor_news_main(file):
    data = load_data(file)

    #unsorted corporate action news
    corp_action = data[data['Other_keywords_present'].notna()].reset_index(drop=True)

    #sorted corporate action news
    corp_action_news = data[data['Other_keywords_present'].notna()].reset_index(drop=True).sort_values(by=['Article_sentiment_score'], ascending=True)

    search_query = st.text_input("Filter/Search", key="2")

    indices = []
    if search_query:
        for index, row in corp_action.iterrows():
            if search_query.lower() in row['summary'].lower() or search_query.lower() in row['Title'].lower():
                indices.append(index)

        news = corp_action.iloc[indices]
    else:
        news = corp_action_news

    for index, row in news.iterrows():
        summary_lines = row['summary'].split('\n') 
        text = st.subheader(f":blue[{row['Title']}]")

        #IF THERE IS RELEVANT securities lending data, all of it will show
        #else just the ticker will show
        if len(eval(row['CUSIP'])) > 0:

            st.caption(f"**Tickers:** {', '.join(eval(row['Tickers']))} **CUSIP:** {', '.join(eval(row['CUSIP']))} **Utilization:** {', '.join([str(i) for i in eval(row['Utilization'])])} **1D Fee:** {', '.join([str(i) for i in eval(row['1_Day_Fee'])])} **10D Fee:** {', '.join([str(i) for i in eval(row['10_Day_Fee'])])}")
        else:
            st.caption(f"**Tickers:** {', '.join(eval(row['Tickers']))}")

        # st.write(collapsed_summary.replace('$', '\$').replace('-', '•\n'))
        st.write('\n'.join(summary_lines).replace('$', '\$'))
        if isinstance(row['Other_keywords_present'],str):
            st.caption(f"**{' | '.join(eval(row['Other_keywords_present']))}**")
        st.divider()


def other_news_main(file):
    data = load_data(file)
    try:
        most = data.groupby('Impact_Level').get_group('Most Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        most = pd.DataFrame()
    try:
        high = data.groupby('Impact_Level').get_group('High Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        high = pd.DataFrame()
    try:
        moderate = data.groupby('Impact_Level').get_group('Moderate Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        moderate = pd.DataFrame()
    try:
        low = data.groupby('Impact_Level').get_group('Low Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        low = pd.DataFrame()
    try:
        least = data.groupby('Impact_Level').get_group('Least Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        least = pd.DataFrame()
    frames = [most, high, moderate, low, least]
    datar = pd.concat(frames).reset_index(drop=True)


    news = pd.DataFrame()
    rel = pd.DataFrame()
    search_query = st.text_input("Filter/Search", key="1")

    rel_indices = []
    for index, row in datar.iterrows():
        if row['is_Relevant'] == 'Not Relevant':
            rel_indices.append(index)

        rel = datar.iloc[rel_indices].reset_index(drop=True)

    indices = []
    if search_query:
        for index, row in rel.iterrows():
            if search_query.lower() in row['summary'].lower() or search_query.lower() in row['Title'].lower():
                indices.append(index)

        news = rel.iloc[indices]
    else:
        news = rel



    for index, row in news.iterrows():
        summary_lines = row['summary'].split('\n')

        text = st.subheader(f":blue[{row['Title']}]")

        #IF THERE IS RELEVANT securities lending data, all of it will show
        #else just the ticker will show
        if len(eval(row['CUSIP'])) > 0:

            st.caption(f"**Tickers:** {', '.join(eval(row['Tickers']))} **CUSIP:** {', '.join(eval(row['CUSIP']))} **Utilization:** {', '.join([str(i) for i in eval(row['Utilization'])])} **1D Fee:** {', '.join([str(i) for i in eval(row['1_Day_Fee'])])} **10D Fee:** {', '.join([str(i) for i in eval(row['10_Day_Fee'])])}")
        else:
            st.caption(f"**Tickers:** {', '.join(eval(row['Tickers']))}")

        st.write('\n'.join(summary_lines).replace('$', '\$'))
        if isinstance(row['Other_keywords_present'],str):
            st.caption(f"**{' | '.join(eval(row['Other_keywords_present']))}**")
        st.divider()

def all_news_main(file):
    data = load_data(file)

    try:
        most = data.groupby('Impact_Level').get_group('Most Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        most = pd.DataFrame()
    try:
        high = data.groupby('Impact_Level').get_group('High Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        high = pd.DataFrame()
    try:
        moderate = data.groupby('Impact_Level').get_group('Moderate Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        moderate = pd.DataFrame()
    try:
        low = data.groupby('Impact_Level').get_group('Low Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        low = pd.DataFrame()
    try:
        least = data.groupby('Impact_Level').get_group('Least Impact').sort_values(by=['Article_sentiment_score'], ascending=True)
    except Exception as e:
        least = pd.DataFrame()
    frames = [most, high, moderate, low, least]
    datar = pd.concat(frames).reset_index(drop=True)

    news = pd.DataFrame()

    search_query = st.text_input("Filter/Search", key="3")

    indices = []
    if search_query:
        for index, row in datar.iterrows():
            if search_query.lower() in row['summary'].lower() or search_query.lower() in row['Title'].lower():
                indices.append(index)

        news = datar.iloc[indices]
    else:
        news = datar

    for index, row in news.iterrows():
        summary_lines = row['summary'].split('\n')
        text = st.subheader(f":blue[{row['Title']}]")

        #IF THERE IS RELEVANT securities lending data, all of it will show
        #else just the ticker will show
        if len(eval(row['CUSIP'])) > 0:

            st.caption(f"**Tickers:** {', '.join(eval(row['Tickers']))} **CUSIP:** {', '.join(eval(row['CUSIP']))} **Utilization:** {', '.join([str(i) for i in eval(row['Utilization'])])} **1D Fee:** {', '.join([str(i) for i in eval(row['1_Day_Fee'])])} **10D Fee:** {', '.join([str(i) for i in eval(row['10_Day_Fee'])])}")
        else:
            st.caption(f"**Tickers:** {', '.join(eval(row['Tickers']))}")

        st.write('\n'.join(summary_lines).replace('$', '\$'))
        if isinstance(row['Other_keywords_present'],str):
            st.caption(f"**{' | '.join(eval(row['Other_keywords_present']))}**")
        st.divider()

if __name__ == "__main__":
    main()
