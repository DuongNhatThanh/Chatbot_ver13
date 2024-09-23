import streamlit as st
from ui.authenticate import register, login, guest_login
from ui.sidebar import show_sidebar

def main():
    show_sidebar()

    if "logged" not in st.session_state:
        with st.expander(label="ARMY SALES CHATBOT", expanded=True):
            login_tab, create_tab, guest_tab = st.tabs(
                [
                    "Đăng nhập",
                    "Tạo tài khoản",
                    "Đăng nhập với tư cách khách",
                ]
            )

            with login_tab:
                login()
            with create_tab:
                register()
            with guest_tab:
                guest_login()   
    else:
        col = st.columns(1)
        with col:
            st.image("")
            if st.button("Hỏi đáp với chatbot"):
                st.switch_page("./ui/pages/1_💬_Chat.py")
            
        st.success("Chatbot đã sẵn sàng để trò chuyện với bạn !!")


if __name__ == "__main__":
    main()