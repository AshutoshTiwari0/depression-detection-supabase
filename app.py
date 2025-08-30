import streamlit as st
import pandas as pd 
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import streamlit_authenticator as stauth
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
def sign_up_user(email, password):
    try:
        user = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return user
    except Exception as e:
        st.error(f"Error signing up: {e}")
        return None

def sign_in_user(email, password):
    try:
        user = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return user
    except Exception as e:
        st.error(f"Error signing in: {e}")
        return None
def sign_out_user():
    try:
        # Server-side sign out
        supabase.auth.sign_out()

        # Clear all user/session info in Streamlit
        for key in ["logged_in", "user", "access_token", "refresh_token"]:
            if key in st.session_state:
                del st.session_state[key]

        # Force rerun so UI updates immediately
        #st.rerun()

    except Exception as e:
        st.error(f"Error signing out: {e}")

#login page 
st.set_page_config(page_title='Depression Detection',page_icon=':guardsman:',layout='centered')

#user authentication

#st.write('Enter credentials to continue.')


def main_app():
    st.title('Depression Detection')


    #taking the input from user
    text=st.text_input(label='Enter the text to analyse depression type',max_chars=200,placeholder='Enter text')

    @st.cache_resource
    def load_model():
        return pickle.load(open("model.pickle", "rb"))

    @st.cache_data
    def load_tfidf():
        return pickle.load(open("tfidf.pickle", "rb"))

    model = load_model()
    tfidf = load_tfidf()

    if text is not None and text!='':
        #making prediction
        vectorized_text=tfidf.transform([text])
        result=model.predict(vectorized_text)[0]

        #showing the predicted label
        st.write(f'The predicted depression type is : {result}')

        #showing the prediction probability
        st.write(f'The prediction probability is : {model.predict_proba(vectorized_text).max().round(2)}')
            #showing the prediction for each class
        results=[]
        for i in model.classes_:
            results.append(model.predict_proba(vectorized_text)[0][list(model.classes_).index(i)])

        df=pd.DataFrame({'Depression Type':model.classes_,'Probability':results})
        st.dataframe(df)

            #making a bar chart
        st.bar_chart(data=df,x='Depression Type',y='Probability')
    else:
        st.warning('Please enter the text to analyse')
        st.stop()
    if st.session_state.get('logged_in'):
        if st.button('Sign Out'):
            sign_out_user()
            st.success('You have been signed out.')
            st.session_state['logged_in']=False
            st.rerun()

def auth_screen():
    st.title('Depression Detection App')
    option=st.selectbox('Select an option', ['Sign In', 'Sign Up'])
    email=st.text_input('Email')
    password=st.text_input('Password', type='password')

    if option=='Sign Up' and st.button('Register'):
        user=sign_up_user(email, password)
        if user and user.user:
            st.success('Sign up successful! Please sign in.')

    if option=='Sign In' and st.button('Login'):
        user=sign_in_user(email, password)
        if user and user.user:
            st.session_state.user_email=user.user.email
            st.success('Sign in successful {email}!')
            st.rerun()

if 'user_email' not in st.session_state:
    st.session_state.user_email=None

if st.session_state.user_email:
    st.write(f'Logged in as {st.session_state.user_email}')
    st.session_state['logged_in']=True
    main_app()
else:
    sign_out_user()
    auth_screen()
