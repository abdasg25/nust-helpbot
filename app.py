import streamlit as st
import os
import time
from log import log_interaction

st.markdown("""
<style>
    /* Light blue background for the entire page */
    .stApp, .main, .block-container, .stApp > div, .stApp > div > div {
        background-color: #e6f0ff !important;
        color: black;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Ensure all sections have the same background */
    .stApp > div > div > div > div > div > div {
        background-color: #e6f0ff !important;
    }

    /* Title bar with deep navy and glow effect */
    h1 {
        background-color: #074880;
        color: white !important;
        padding: 0.6rem 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        text-align: center;
        letter-spacing: 1px;
    }

    /* Logo container styling */
    img {
        background-color: #074880;
        padding: 0.4rem;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }

    /* Buttons */
    .stButton>button {
        background-color: #074880;
        color: white;
        border-radius: 8px;
        padding: 0.4rem 1rem;
        font-weight: 600;
        transition: 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #055072;
        transform: scale(1.03);
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    /* Dropdowns and input text */
    label, .stSelectbox label, .stTextInput label {
        color: black !important;
        font-weight: 600;
    }

    .stSelectbox div[data-baseweb="select"] {
        border: 1px solid #074880;
        border-radius: 8px;
        background-color: #ffffff;
    }

    /* Answer box styling */
    .stMarkdown div[style*="background: #f4f6fa"] {
        background: #ffffff;
        border-left: 5px solid #074880;
        padding: 1rem;
        color: black;
        border-radius: 10px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Footer text */
    footer, .footer {
        color: #074880;
        font-size: 0.95rem;
        margin-top: 2em;
    }
</style>
""", unsafe_allow_html=True)


def get_data_folders(path="data"):
    try:
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    except Exception:
        return []

st.set_page_config(page_title="NUST HELP BOT", page_icon="NUST_logo.png", layout="centered")

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.image("NUST_logo.png", width=100, output_format="PNG")

st.markdown("<div style='margin-top: -40px;'></div>", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; font-size: 2.5rem; font-weight: 700; letter-spacing: 1px; margin-top: 0;'>NUST HELP BOT</h1>
""", unsafe_allow_html=True)



col1, col2 = st.columns(2)

with col2:
    st.markdown("<div style='font-size: 1.1rem; margin-bottom: 0.3em;'>Select Handbook:</div>", unsafe_allow_html=True)
    data_folders = get_data_folders("data")
    def to_option(name):
        return name.replace('_', ' ')
    options = [to_option(name) for name in data_folders]
    selected_bot = st.selectbox("Select Handbook", options, label_visibility="collapsed", key="bot_select",
        help="Choose a bot (from data folders)")

with col1:
    st.markdown("<div style='font-size: 1.1rem; margin-bottom: 0.3em;'>Upload PDF:</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        try:
            # Create folder name from the uploaded file name (without extension)
            folder_name = os.path.splitext(uploaded_file.name)[0]
            folder_name = "".join(c if c.isalnum() or c in ' _-' else '_' for c in folder_name)
            folder_path = os.path.join("data", folder_name)
            
            # Remove existing folder if it exists
            if os.path.exists(folder_path):
                import shutil
                shutil.rmtree(folder_path)
            
            # Create new folder
            os.makedirs(folder_path, exist_ok=True)
            
            # Save the uploaded file
            file_path = os.path.join(folder_path, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"Successfully uploaded {uploaded_file.name} to {folder_name}")
            
            # Refresh the page to show the new folder in the selectbox
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")


from db_utils import get_or_build_bot_db_path
from query_data import query_rag

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type your message..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        followup_questions = []
        
        # Get the folder name for the selected bot
        folder_map = {to_option(name): name for name in data_folders}
        folder_name = folder_map.get(selected_bot)
        
        if folder_name:
            with st.spinner("Checking/Building knowledge base..."):
                db_path = get_or_build_bot_db_path(folder_name)
            
            with st.spinner("Thinking..."):
                start_time = time.time()
                
                # Create context from conversation history
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages[-4:]])
                
                # Query with context and request follow-up questions
                response = query_rag(
                    f"Previous conversation context:\n{context}\n\nCurrent question: {prompt}", 
                    db_path,
                    get_followups=True  # Request follow-up questions
                )
                end_time = time.time()
                time_taken = round(end_time - start_time, 3)
                
                full_response = response.get("response", "No response generated.")
                followup_questions = response.get("followup_questions", [])
                
                log_interaction(prompt, full_response, time_taken)
        else:
            full_response = "Could not find selected bot's folder."
        
        # Add assistant response to chat history (without follow-up questions)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Display the response
        message_placeholder.markdown(full_response)
        
        # Display follow-up questions as buttons if available
        if followup_questions and len(st.session_state.messages) > 0:
            st.markdown("\n**Suggested follow-up questions:**")
            cols = st.columns(3)  # Create 3 columns for the buttons
            
            for i, question in enumerate(followup_questions[:3]):  # Show max 3 questions
                with cols[i % 3]:
                    if st.button(
                        question,
                        key=f"followup_{i}_{hash(question)}",
                        use_container_width=True,
                        help=f"Ask: {question}"
                    ):
                        # Add the question to the chat when clicked
                        st.session_state.messages.append({"role": "user", "content": question})
                        st.rerun()  # Rerun to process the new message

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; font-size: 1rem; margin-top: 2em;'>
    This is an alpha version of this software, Developed at <b>HPC Lab, NUST-SEECS</b><br>
    <span style='font-size:0.9rem;'><a href='#' style='color:#0066cc;'></a></span>
</div>
""", unsafe_allow_html=True)
