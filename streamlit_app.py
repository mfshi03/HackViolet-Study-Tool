import pandas as pd
import os
import urllib
import re
import requests
import json
import time
import validators
import streamlit as st
from gpt_index import GPTTreeIndex
from gpt_index.readers.schema.base import Document

DIFFBOT = st.secrets["DIFFBOT"]
OPEN_AI_KEY = st.secrets["OPEN_AI_KEY"]
os.environ["OPENAI_API_KEY"] = OPEN_AI_KEY

def find_values(id:str, json_repr:str) -> str:
    '''
    Finds relevant info from JSON text
    '''
    results = []

    def _decode_dict(a_dict):
        try:
            results.append(a_dict[id])
        except KeyError:
            pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict) # Return value ignored.
    return results


@st.cache(persist=True)
def crawl(url:str) -> str:
    '''
    This returns a string of all important text on a webpage
    '''
    crawl_url = url 
    query_url = crawl_url = urllib.parse.quote(crawl_url)
    request_url = "https://api.diffbot.com/v3/article?token=" + DIFFBOT +  "&url=" + query_url
    headers = {"accept": "application/json"}

    response = requests.get(request_url, headers=headers)
    text = "No text"

    if response.status_code == 200:
        if "errorCode" in response.text:
            request_url = "https://api.diffbot.com/v3/discussion?token=" + DIFFBOT +  "&url=" + crawl_url
            headers = {"accept": "application/json"}
            response = requests.get(request_url, headers=headers)
        if "errorCode" in response.text:
            request_url = "https://api.diffbot.com/v3/analyze?token=" + DIFFBOT +  "&url=" + crawl_url 
            headers = {"accept": "application/json"}
            response = requests.get(request_url, headers=headers)
        data = response.text
        title = []
        text = ""
        latent_text = " ".join(find_values('text', data))
        summary = " ".join(find_values('summary',data))
        title =  " ".join(find_values('title', data))
        
    
    text += "Title:" + title + "\n\n" if len(title) > 3 else ""
    text += "Summary:" + summary + "\n\n" if len(summary) > 3 else ""
    text += "Text:" + latent_text if len(latent_text) > 3 else ""

    text = re.sub(' +', ' ', text)
    return text


"""
### HackViolet App
Your study tool
"""


url = st.text_input('Enter a link')
update_link = st.button("Update Link")
query = st.text_input('Now ask a question about the text (add a question mark)')
update_query = st.button("Update Query")


if update_link:
    with st.spinner('Reading your website...'):
        if validators.url(url):
            text = crawl(url)
            time.sleep(5)
        else:
            st.write("Invalid URL")
    st.success("Website Read!!!")
    st.write("Your scraped text preview:", text[0:500])
    st.session_state["text"] = text
    with st.spinner('Indexing your text ....'):
        st.session_state["index"] = GPTTreeIndex([Document(text)])
        time.sleep(5)
    st.success("Your text has been indexed")

if update_query:
    with st.spinner("Thinking..."):
        answer = st.session_state["index"].query(query, verbose=True)
        st.session_state["answer"] = answer
        time.sleep(5)
    st.success("Your answer was found")
    st.write("Your answer:", st.session_state["answer"])
    

text = ''
scraped = False
if validators.url(url) and "?" in query: 
    st.write("Your link is:", url)
    with st.spinner('Wait for it...'):
        text = crawl(url)
        time.sleep(5)