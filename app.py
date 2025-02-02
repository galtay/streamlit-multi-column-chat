import time

from litellm import completion
import streamlit as st


LOREM_IPSUM = """\
Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit
in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui
officia deserunt mollit anim id est laborum."""

st.set_page_config(layout="wide")


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []


init_session_state()


def mock_response_generator():
    response = LOREM_IPSUM
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


def llm_gen(messages, mock=False):
    if mock:
        for token in mock_response_generator():
            yield token
    else:
        response = completion(
            model="openai/gpt-4o-mini", messages=messages, stream=True
        )
        for part in response:
            yield part.choices[0].delta.content or ""


def reset_chat():
    st.session_state["messages"] = []


with st.sidebar:

    with st.container(border=True):
        st.write("Layout Options")

        left_ratio = st.slider(
            "Adjust column widths",
            min_value=0.2,
            max_value=0.8,
            value=0.6,
            step=0.1,
            help="Drag to adjust the width ratio between chat and visualization panels",
        )
        right_ratio = 1 - left_ratio

        message_container_height = st.slider(
            "Adjust chat height",
            min_value=100,
            max_value=1600,
            value=750,
            step=20,
            help="Adjust the height of the container for messages",
        )

    with st.container(border=True):
        st.write("Chat Options")
        st.button("New Chat", on_click=reset_chat)
        mock_llm = st.toggle("Mock LLM Calls", True)


left_col, right_col = st.columns([left_ratio, right_ratio])

with left_col:

    messages_container = st.container(height=message_container_height)

    with messages_container:
        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if query := st.chat_input():
        message = {"role": "user", "content": query}
        with messages_container:
            with st.chat_message("user"):
                st.markdown(query)
        st.session_state["messages"].append(message)

        with messages_container:
            with st.chat_message("assistant"):
                response = st.write_stream(
                    llm_gen(st.session_state["messages"], mock=mock_llm)
                )
        st.session_state.messages.append({"role": "assistant", "content": response})
