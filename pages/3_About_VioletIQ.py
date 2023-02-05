import requests
import streamlit as st
from streamlit_lottie import st_lottie

st.set_page_config(page_title="About VioletIQ", page_icon=":sparkles:", layout="centered")

#-loads the animations
def load_lottieAnimation(url):
    request = requests.get(url)
    if request.status_code != 200:
        return None
    return request.json()

#-Assets/Animations
lottie_learning = load_lottieAnimation("https://assets3.lottiefiles.com/packages/lf20_xxyvtiab.json")
lottie_reason = load_lottieAnimation("https://assets4.lottiefiles.com/private_files/lf30_vAtD7F.json")
lottie_better = load_lottieAnimation("https://assets5.lottiefiles.com/packages/lf20_8autcbbt.json")
lottie_teamwork = load_lottieAnimation("https://assets8.lottiefiles.com/packages/lf20_fclga8fl.json")

#-What is VioletIQ
with st.container():    
    left_column, right_column = st.columns(2)
    with left_column:
        st.title("What is VioletIQ?")
        st.write("##")
        st.write(
            """
            VioletIQ is multifaceted learning website that allows anyone
            to enter a link and ask a question about the text in the link
            for further clarificiation. VioletIQ also has an additional
            bias detector that detects sexism from the text in the link
            using an trained model. Another great feature from VioletIQ
            is that it generates flash cards based off of what your queries
            and submitted links.
            """
        )
    with right_column:
        st_lottie(lottie_learning)  

#-Why did we make VioletIQ
with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        st.title("Why did we make VioletIQ?")
        st.write("##")
        st.write(
            """
            We designed VioletIQ in order to help anyone with a passion
            for learning to be able to learn anything no matter their
            education level. We made the bias detector because we noticed
            a large amount of sexism and gender bias in a lot of text on
            the internet and we wanted to make a tool that would allow for
            people to know whether a text or article is sexist. We wanted to
            use our passion for coding as a gateway for people who may not 
            have the chance or opportunity to learn, and we also wanted
            to give people the knowledge of whether their learning material
            on the internet is sexist or not. 
            """
        )
    with right_column:
        st_lottie(lottie_reason)

#-Why use VioletIQ
with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        st.title("Why use VioletIQ?")
        st.write("##")
        st.write(
            """
         VioletIQ is better than its competitors because:
            - It fits whatever criteria you have and you can ask it anything
            - It provides information about whether a document is sexist using a top of the line trained model
            - It is all in one website
            - It is free for everyone and it is simple for anyone to use
            """
        )
    with right_column:
        st_lottie(lottie_better)

#-About the Team
with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        st.title("About the Team")
        st.write("##")
        st.write(
            """
            Our team consists of 4 students at Virginia Tech that have a lot of passion
            for using their knowledge of coding to make the world a better place. All of 
            us have different specialties, but using our diverse skillsets, we have made
            the best product that would not have been made by ourselves. We are constantly
            trying to improve our products even outside the competition as 
            hackathons are not just about winning prizes. We hope to be able to consistently
            produce quality software at any chance we get!
            """
        )
    with right_column:
        st_lottie(lottie_teamwork)