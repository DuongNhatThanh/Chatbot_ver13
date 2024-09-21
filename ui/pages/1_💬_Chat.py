import streamlit as st
from typing import List, Dict
from source.chat_cp import chat_interface
from configs.config_system import SYSTEM_CONFIG
from ui.sidebar import show_sidebar 




def main():
    show_sidebar()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        username = st.session_state.username
        # user_info = st.session_state.user_info
        seasion_id = st.session_state.seasion_id
        st.subheader("")
        container = st.container()
        chat_interface(user_name=username, seasion_id=seasion_id, container=container)

if __name__ == "__main__":
    main()