import pandas as pd
import os
import urllib
import re
import requests
import json
import time
import validators
import streamlit as st
import openai
from gpt_index import GPTTreeIndex
from gpt_index.readers.schema.base import Document

"""
### HackViolet App
    Detect sexism in passages
"""


DIFFBOT = st.secrets["DIFFBOT"]
OPEN_API_KEY = st.secrets["OPEN_API_KEY"]
os.environ["OPENAI_API_KEY"] = OPEN_API_KEY

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
        
    text += "Text:" + latent_text if len(latent_text) > 3 else ""

    text = re.sub(' +', ' ', text)
    return text

def generatePrompt(base_prompt: str) -> str:
    '''
    prepends examples to prompt.
    '''
    prefix = 'Generate questions and answers about the following text: '
    suffix = "Answer: "
    return prefix + base_prompt + suffix

url = st.text_input('Enter a link')
update_link = st.button("Update Link")

if update_link:
    with st.spinner('Reading your website...'):
        if validators.url(url):
            text = crawl(url)
            time.sleep(5)
        else:
            st.write("Invalid URL")
    st.success("Website Read!!!")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = generatePrompt(text[:3000])
    print(prompt)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.3,
        max_tokens=3000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    answer = str(response["choices"][0]["text"])
    st.subheader("These biased spans of text were detected:")
    answers = answer.split(' <SEP> ')
    for answer in answers:
        st.code(answer, language="english")
    # https://twitter.com/stuffmadehere
    # who is stuffmadehere?
    # https://www.theguardian.com/technology/2022/aug/06/andrew-tate-violent-misogynistic-world-of-tiktok-new-star