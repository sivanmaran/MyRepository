import streamlit as st
from generate_sql import generate_sql

st.set_page_config(
    page_title="NL2SQL Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("NL2SQL Agent")
st.write("Ask a question about your data")

question = st.text_input(
    "Enter your question",
    placeholder="Example: What is the total revenue by region?"
)

if st.button("Submit"):

    if not question:
        st.warning("Please enter a question.")

    else:
        try:
            with st.spinner("Generating SQL..."):
                sql = generate_sql(question)

            st.subheader("Generated SQL")
            st.code(sql, language="sql")

        except Exception as e:
            st.error(f"Error: {e}")