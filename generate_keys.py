import pickle
import streamlit_authenticator as stauth
from pathlib import Path

names=['Ashutosh Tiwari','Abhishek Mathur', 'Guest User']
usernames=['Ash','Kenshi','Guest']
passwords=['Ashutosh','Abhishek','Guest']

#converting plain passwords to hashed passwords
hashed_passwords=stauth.Hasher().hash_list(passwords) #this uses bcrypt algorithm
file_path=Path(__file__).parent/'hashed_pw.pkl' #our hashed passwords will be stored in this file
with file_path.open('wb') as file:
    pickle.dump(hashed_passwords,file)