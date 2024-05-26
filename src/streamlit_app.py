import streamlit as st
from hugchat import hugchat
from chat.chat import load_model, unload_model, get_response
import os

# App title
st.set_page_config(page_title="MEDAL-AI")
MODEL_DIR = os.getcwd() + "/models/"

def list_model_files(directory):
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return []

# Hugging Face Credentials
with st.sidebar:
    st.title('MEDAL-AI')
    st.markdown('📖 Medical Expert for Diagnostic Accuracy and Learning 📖')
    model_files = list_model_files(MODEL_DIR)
    model_files = [None] + model_files
    selected_model = st.selectbox('Select Model',options=model_files)
    
    # Load and Unload buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Load'):
            with st.spinner('Loading...'):
                load_model(MODEL_DIR + selected_model)
                st.session_state['loaded_model'] = selected_model
                st.success(f"Model '{selected_model}' loaded!")
    with col2:
        if st.button('Unload'):
            with st.spinner('Unloading...'):
                if 'loaded_model' in st.session_state:
                    unload_model()
                    st.success(f"Model '{st.session_state['loaded_model']}' unloaded!")
                    del st.session_state['loaded_model']
                else:
                    st.warning('No model is currently loaded.')
    
    st.container(height=425, border=0)
    if st.button('Clear'):
        st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]
    
    
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    assistant_message = {"role": "assistant", "content": ""}
    st.session_state.messages.append(assistant_message)

    message_placeholder = st.empty()
    

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            def process_chunks(chunk):
                assistant_message["content"] += chunk
                message_placeholder.markdown(assistant_message["content"])
            response = get_response(prompt, process_chunks) 

            # st.write(response) 
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
