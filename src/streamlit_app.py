import streamlit as st
from hugchat import hugchat
from chat.chat import load_model, unload_model, get_response
import streamlit.components.v1 as components
import os

# Set up app title and layout
st.set_page_config(page_title="MEDAL-AI", layout="wide", page_icon="📖", menu_items=None)
MODEL_DIR = os.getcwd() + "/models/"

def custom_loading():
    loader_html = """
    <div class="loader">Loading...</div>
    <style>
    .loader {
      font-size: 20px;
      color: #2e86c1;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    </style>
    """
    components.html(loader_html, height=100)


hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

def list_model_files(directory):
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return []

@st.cache_resource
def load_data():
    model_files = list_model_files(MODEL_DIR)
    return load_model(MODEL_DIR + model_files[0])

# Display the custom loading indicator
placeholder = st.empty()
with placeholder.container():
    custom_loading()

# Load data
data = load_data()
placeholder.empty()  # Clear the loading indicator once data is loaded

# Sidebar setup
with st.sidebar:
    st.title('MEDAL-AI')
    st.markdown('📖 Medical Expert for Diagnostic Accuracy and Learning 📖')
    model_files = list_model_files(MODEL_DIR)
    model_files = [None] + model_files

    st.container(height=525, border=0)
    if st.button('Clear'):
        st.session_state.messages = [{"role": "assistant", "content": "I am MEDAL-AI. How may I help you?"}]

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I am MEDAL-AI. How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input prompt and handle user input
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if the last message is not from the assistant
if st.session_state.messages[-1]["role"] != "assistant":
    assistant_message = {"role": "assistant", "content": ""}
    st.session_state.messages.append(assistant_message)

    message_placeholder = st.empty()

    with message_placeholder.container():
        with st.chat_message("assistant"):
            assistant_content_placeholder = st.empty()

            def process_chunks(chunk):
                st.session_state.messages[-1]["content"] += chunk
                assistant_content_placeholder.markdown(st.session_state.messages[-1]["content"])

            response = get_response(prompt, process_chunks)
            st.session_state.messages[-1]["content"] = response
            assistant_content_placeholder.markdown(response)

# Custom CSS for better styling
st.markdown("""
    <style>
        .stTextInput textarea {
            font-size: 16px;
        }
        .stButton button {
            background-color: #2e86c1;
            color: white;
        }
        .stMarkdown pre {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)
