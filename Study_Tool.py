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

DIFFBOT = st.secrets["DIFFBOT"]
OPEN_API_KEY = st.secrets["OPEN_API_KEY"]
os.environ["OPENAI_API_KEY"] = OPEN_API_KEY



if 'history' not in st.session_state:
   st.session_state["history"] = []

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

@st.experimental_singleton(show_spinner=False)
def store_index(Documents: list[Document]):
    return GPTTreeIndex(Documents)


@st.experimental_memo(show_spinner=False) #@st.cache(persist=True)
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

@st.experimental_memo(show_spinner=False)
def answer_question(_index, query):
    return _index.query(query, verbose=True)


"""
### VioletIQ
    Your study tool
"""



url = st.text_input('Enter a link')
update_link = st.button("Update Link")
query = st.text_input('Now ask a question about the text (add a question mark)')
update_query = st.button("Ask")

question = query #new line


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
        st.session_state["index"] = store_index([Document(text)])
        time.sleep(5)
    st.success("Your text has been indexed")

if update_query:
    with st.spinner("Thinking..."):
        answer = answer_question(st.session_state["index"], query)
        st.session_state["answer"] = answer
        time.sleep(5)
    st.success("Your answer was found")
    st.write("Your answer:", st.session_state["answer"])

    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Identify the entities comma separated and no incomplete entities:" + str(st.session_state["answer"]),
        temperature=0.3,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    answer = str(st.session_state["answer"])
    search = "https://en.wikipedia.org/w/index.php?search="
    entities = response["choices"][0]["text"].strip().split(",")
    #answer_sep = answer.split(" ")
    print(entities)
    for i in range(len(entities)):
        entities[i] = entities[i].strip().lower()
        print(entities[i])
        if entities[i] in answer and entities[i].replace(" ", "") != "":
            print("works")
            query = entities[i].replace(" ","+")
            answer = answer.replace(entities[i], "[" + entities[i] + "](" +  search +  query+ ")")

    #print(answer)
    st.markdown("Your answer with links:" + answer)
    #https://twitter.com/stuffmadehere
    # who is stuffmadehere?

    st.session_state.history.append({"Link": url, "Questions": question, "Results": answer}) #new line

    



text = ''
scraped = False
if validators.url(url) and "?" in query: 
    st.write("Your link is:", url)
    with st.spinner('Wait for it...'):
        text = crawl(url)
        time.sleep(5)

placeholder = st.empty() #new line
  
with placeholder.container():
   st.write(pd.DataFrame( st.session_state.history)) #new line


if st.button("Clear History"):
       placeholder =  st.empty()
       st.session_state.history = []
       