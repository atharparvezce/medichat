import streamlit as st

def main():
    st.title("Medi Chat !")

    prompt=st.chat_input("Pass your prompt here")

    if prompt:
        st.chat_message('user').markdown(prompt)

        response="Hi I am MediChat!"

        st.chat_message('assistant').markdown(response)

if __name__=="__main__":
    main()