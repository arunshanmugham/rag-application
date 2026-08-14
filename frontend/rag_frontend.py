import streamlit as st
import requests

st.title("🔬 Local RAG Architecture Test Lab")

user_input = st.text_input("Ask a test question (e.g., Try a simple policy question vs. a complex comparative one):")
BACKEND_URL = "http://127.0.0.1:8000"

if st.button("Run Test Pipeline"):
    if user_input:
        with st.spinner("Processing local pipeline routing logic..."):
            # Call your local FastAPI server running on port 8000
            response = requests.post(f"{BACKEND_URL}/api/ask", json={"question": user_input})
            
            if response.status_code == 200:
                data = response.json()
                
                # Highlight which path the routing layer chose!
                path = data["path_used"]
                if path == "DIRECT_RAG":
                    st.success(f"🎯 Route Target: {path} (Fast, Low Cost)")
                else:
                    st.warning(f"🧠 Route Target: {path} (Heavy Agent Loop)")
                
                st.markdown("### Generated Answer:")
                st.write(data["answer"])
            else:
                st.error(f"Error from local backend: {response.text}")
