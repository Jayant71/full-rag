import streamlit as st
import requests
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG System", layout="wide")

st.title("Retrieval Augmented Generation (RAG)")

# --- Sidebar: Space Management ---
with st.sidebar:
    st.header("Spaces")
    
    # Create New Space
    new_space_name = st.text_input("New Space Name")
    if st.button("Create Space"):
        if new_space_name:
            try:
                res = requests.post(f"{BACKEND_URL}/spaces", params={"name": new_space_name})
                if res.status_code == 200:
                    st.success(f"Created space: {new_space_name}")
                    st.rerun()
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    st.divider()

    # List Spaces
    try:
        res = requests.get(f"{BACKEND_URL}/spaces")
        if res.status_code == 200:
            spaces = res.json()
            space_options = {s["name"]: s["id"] for s in spaces}
            
            selected_space_name = st.selectbox(
                "Select Space", 
                options=list(space_options.keys()) if spaces else [],
                index=0 if spaces else None
            )
            
            if selected_space_name:
                st.session_state.active_space_id = space_options[selected_space_name]
                st.session_state.active_space_name = selected_space_name
            else:
                st.session_state.active_space_id = None
        else:
            st.error("Failed to fetch spaces")
            st.session_state.active_space_id = None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        st.session_state.active_space_id = None

# --- Main Content ---

if not st.session_state.get("active_space_id"):
    st.info("Please create or select a Space from the sidebar to continue.")
    st.stop()

st.header(f"Space: {st.session_state.active_space_name}")
active_space_id = st.session_state.active_space_id

# --- Document Management ---
with st.expander("Manage Documents", expanded=True):
    # 1. Upload
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload documents (Max 5)", 
        type=["pdf", "docx", "txt", "md", "csv"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if len(uploaded_files) > 5:
            st.error("Please upload a maximum of 5 files at a time.")
        else:
            if st.button("Ingest Files"):
                with st.spinner("Ingesting..."):
                    files = [
                        ("files", (f.name, f, f.type)) for f in uploaded_files
                    ]
                    try:
                        response = requests.post(f"{BACKEND_URL}/ingest/{active_space_id}", files=files)
                        if response.status_code == 200:
                            results = response.json()
                            for res in results:
                                st.success(f"{res['filename']}: {res['message']}")
                            st.rerun()
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

    st.divider()

    # 2. List & Delete
    st.subheader("Ingested Documents")
    try:
        res = requests.get(f"{BACKEND_URL}/spaces/{active_space_id}/documents")
        if res.status_code == 200:
            documents = res.json()
            if documents:
                for doc in documents:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.text(doc["filename"])
                    with col2:
                        if st.button("Delete", key=f"del_{doc['id']}"):
                            with st.spinner("Deleting..."):
                                del_res = requests.delete(f"{BACKEND_URL}/spaces/{active_space_id}/documents/{doc['id']}")
                                if del_res.status_code == 200:
                                    st.success(f"Deleted {doc['filename']}")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to delete: {del_res.text}")
            else:
                st.info("No documents in this space.")
        else:
            st.error("Failed to fetch documents.")
    except Exception as e:
        st.error(f"Connection Error: {e}")


# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# We should ideally fetch history from backend on space switch, but for now let's just clear local state if space changes
if "last_space_id" not in st.session_state or st.session_state.last_space_id != active_space_id:
    st.session_state.messages = []
    st.session_state.last_space_id = active_space_id

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("View Sources"):
                for source in message["sources"]:
                    st.markdown(f"**Score:** {source['score']}")
                    st.markdown(f"**Text:** {source['text']}")
                    st.markdown("---")

if prompt := st.chat_input("Ask a question about your documents"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "query": prompt,
                    # We don't need to send chat_history as backend fetches it from DB now
                    "chat_history": [] 
                }
                response = requests.post(f"{BACKEND_URL}/chat/{active_space_id}", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data["sources"]
                    
                    st.markdown(answer)
                    with st.expander("View Sources"):
                        for source in sources:
                            st.markdown(f"**Score:** {source['score']}")
                            st.markdown(f"**Text:** {source['text']}")
                            st.markdown("---")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")


