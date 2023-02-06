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
import pandas as pd
from gpt_index import GPTTreeIndex
from gpt_index.readers.schema.base import Document

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


@st.cache(persist=True, show_spinner=False)
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
    prefix = 'Identify sections of the prompt text that are sexist. If there are no sexist sections, only output "None found.". Prompt: Andrew Tate says women belong in the home, can’t drive, and are a man’s property. He also thinks rape victims must “bear responsibility” for their attacks and dates women aged 18–19 because he can “make an imprint” on them, according to videos posted online. In other clips, the British-American kickboxer – who poses with fast cars, guns and portrays himself as a cigar-smoking playboy – talks about hitting and choking women, trashing their belongings and stopping them from going out. Answer: women belong in the home, can’t drive, and are a man’s property <SEP> rape victims must “bear responsibility” for their attacks <SEP> talks about hitting and choking women, trashing their belongings and stopping them from going out. Prompt: '
    # prefix = 'Identify sections of the prompt text that are sexist'
    # suffix = "Answer: "
    return prefix + base_prompt

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

    with st.spinner("Identifying sexist text..."):
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
        time.sleep(5)
    
    answer = str(response["choices"][0]["text"])
    st.subheader("These biased spans of text were detected:")
    answers = answer.split(' <SEP> ')
    arr = []
    text = text[0:3000]

    sexist = [0 for i in range(0,len(text), 30)]
    for answer in answers:
        print(text.find(answer)//30)
        val = 0 if text.find(answer)//30 < 0 else text.find(answer)//30
        val = 99 if val > 100 else val
        sexist[val] = 1
        st.code(answer, language="english")
    
    df = pd.DataFrame({"data": sexist})
    df['data'][0] = max(0, df['data'][0] - 1)
    df['average'] = df['data'].rolling(3).mean()
    st.subheader("Sexist text distribution from beginning to end:")
    st.line_chart(df['average'])
    #https://twitter.com/stuffmadehere
    # who is stuffmadehere?