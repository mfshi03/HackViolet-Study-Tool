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
    Generates Flashcards from your text
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

def parse_to_dict(content: str, text: str) -> dict[str, str]:
    lines = content.strip().split("\n")

    questions = []
    answers = []

    for line in lines:
        if "Q" == line[0:1]:
            parts = line.split(":")
            question = parts[1]
            questions.append(question)

        if "A" == line[0:1]:
            parts = line.split(":")
            answer = parts[1]
            answers.append(answer)


    while len(questions) != len(answers):
        if len(questions) > len(answers):
            del questions[:-1]
        else:
            del answers[:-1]

    flash = dict()
    flash['answers'] = answers
    flash['questions'] = questions
    return flash

def gen_QA(query:str, length:int=100) -> dict[str,str]:
    prompt = "Generate a list of study questions and answers in the form (Q:Question A:Answer) for the text: " + query
    completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=length,
        temperature=0.3,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    text = completion["choices"][0]["text"]
    print(text)
    dictionary = parse_to_dict(text,query)
    return dictionary

url = st.text_input('Enter a link')
update_link = st.button("Generate")

if update_link:
    with st.spinner('Reading your website...'):
        if validators.url(url):
            text = crawl(url)
            time.sleep(5)
        else:
            st.write("Invalid URL")
    st.success("Website Read!!!")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    flashcards = gen_QA(text[:10000],length=300)
    back = flashcards["answers"]
    front = flashcards["questions"]
    length = 3 if 3 <= len(back) else len(back)
    for i in range(0, length):
        with st.expander(front[i]):
            st.write(back[i])


    # https://twitter.com/stuffmadehere
    # who is stuffmadehere?
    # https://www.theguardian.com/technology/2022/aug/06/andrew-tate-violent-misogynistic-world-of-tiktok-new-star