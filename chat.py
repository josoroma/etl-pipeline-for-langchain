import os
import weaviate
import openai
from pydantic import BaseModel
import streamlit as st

DEFAULT_ASSISTANT_PROMPT = "How can I help you?"
GENERATE_PROMPT = "Act as an experienced and helpful Python and developer, please suggest code from the following response or content: {content}"
# GENERATE_PROMPT = "Given the following response or content, suggest code: {content}"

class Document(BaseModel):
    """
    Pydantic model for a Document.

    Attributes:
    content: str
        The content of the Document.
    """

    content: str

class QueryResult(BaseModel):
    """
    Pydantic model for a QueryResult.

    Attributes:
    document: Document
        The Document object in the QueryResult.
    """

    document: Document

class ChatApp:
    """
    Main application class for managing the Streamlit Chat App.

    Attributes:
    client: weaviate.Client
        The Weaviate client for querying the Weaviate instance.
    OPENAI_API_KEY: str
        The OpenAI API key.
    WEAVIATE_HOST: str
        The host URL of the Weaviate instance.
    WEAVIATE_AUTH_API_KEY: str
        The authentication API key for the Weaviate instance.
    """

    def __init__(self):
        self.client = None
        self.get_env_variables()
        self.client = self.get_client()

    def get_env_variable(self, var_name):
        """
        Get the environment variable value.

        Args:
        var_name (str): Name of the environment variable

        Returns:
        str: Value of the environment variable
        """
        var_value = os.getenv(var_name)
        return var_value

    def get_env_variables(self):
        """
        Get all the required environment variables for the chat application.
        """
        with st.sidebar:
            self.OPENAI_API_KEY = self.get_env_variable("OPENAI_API_KEY") or st.text_input("OpenAI API Key", type="password")
            self.WEAVIATE_HOST = self.get_env_variable("WEAVIATE_HOST") or st.text_input("Weaviate Host")
            self.WEAVIATE_AUTH_API_KEY = self.get_env_variable("WEAVIATE_AUTH_API_KEY") or st.text_input("Bearer Token", type="password")

        if not self.OPENAI_API_KEY or not self.WEAVIATE_HOST or not self.WEAVIATE_AUTH_API_KEY:
            st.info("Please add your OpenAI API Key, Weaviate Host, and Bearer Token to continue.")
            st.stop()

        openai.api_key = self.OPENAI_API_KEY

    def get_client(self):
        """
        Create and get the Weaviate client.

        Returns:
        weaviate.Client: The Weaviate client
        """
        try:
            # https://weaviate.io/developers/weaviate/client-libraries/python
            client = weaviate.Client(
                url=self.WEAVIATE_HOST,
                auth_client_secret=weaviate.AuthApiKey(self.WEAVIATE_AUTH_API_KEY),
                additional_headers={"X-OpenAI-Api-Key": self.OPENAI_API_KEY},
            )
        except Exception as e:
            st.error(f"Error occurred while creating the Weaviate client: {str(e)}")
            st.stop()

        return client

    def client_query(self, question: str):
        """
        Query the Weaviate Vectorstore via the Weaviate client.

        Args:
        question (str): The user's question

        Returns:
        dict: The response from the Weaviate client
        """
        generatePrompt = GENERATE_PROMPT
        nearText = {"concepts": [f"{question}"]}

        with st.spinner("Waiting for the response..."):
            try:
                # https://weaviate.io/developers/weaviate/search/generative
                response = (
                    self.client.query
                    .get("Document", ["content"])
                    .with_generate(single_prompt=generatePrompt)
                    .with_near_text(nearText)
                    .with_limit(3)
                    .do()
                )
            except Exception as e:
                st.error(f"Error occurred while querying the Weaviate client: {str(e)}")
                st.stop()

        return response

    def main(self):
        """
        Main function to run the chat application.
        """
        if "messages" not in st.session_state.keys():
            st.session_state["messages"] = []

        st.chat_message("assistant").write(DEFAULT_ASSISTANT_PROMPT)

        if prompt := st.chat_input("Your prompt:"):
            st.session_state.messages.append({"role": "user", "content": prompt})

            response = self.client_query(prompt)

            if response:
                try:
                    for document in response['data']['Get']['Document']:
                        try:
                            generativeOpenAI = document['_additional']['generate']["singleResult"]
                            content = document['content']
                        except KeyError as ke:
                            st.markdown(f"Error: Expected keys not found in the document. {ke}")
                            continue

                        if content:
                            st.session_state.messages.append({"role": "help", "content": "Semantic Search Response:"})
                            st.session_state.messages.append({"role": "assistant", "content": content})

                        if generativeOpenAI:
                            st.session_state.messages.append({"role": "help", "content": "Generative Open AI Response:"})
                            st.session_state.messages.append({"role": "assistant", "content": generativeOpenAI})

                except KeyError as ke:
                    st.markdown(f"Error: Expected keys not found in the response. {ke}")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

if __name__ == "__main__":
    ChatApp().main()
