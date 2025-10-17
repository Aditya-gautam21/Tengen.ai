"""
Streamlit Cloud Deployment App
Alternative deployment option for Tengen.ai
"""

import streamlit as st
import requests
import json
import os
from typing import Dict, Any

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://tengen-ai-api.example.com")
STREAMLIT_TITLE = "Tengen.ai - AI Research Assistant"

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_TITLE,
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def call_api(endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call the backend API"""
    try:
        url = f"{API_BASE_URL}/api/v1{endpoint}"
        
        if data:
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {"error": str(e)}

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🔬 Tengen.ai")
    st.markdown("**AI-Powered Research Assistant**")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Chat & Inference", "Code Generation", "Research", "Health Status"]
        )
        
        st.header("Settings")
        api_key = st.text_input(
            "Google API Key",
            type="password",
            help="Enter your Google Gemini API key"
        )
        
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
    
    # Main content based on selected page
    if page == "Chat & Inference":
        chat_page()
    elif page == "Code Generation":
        code_generation_page()
    elif page == "Research":
        research_page()
    elif page == "Health Status":
        health_status_page()

def chat_page():
    """Chat and inference page"""
    st.header("💬 Chat & Inference")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = call_api("/predict", {
                    "prompt": prompt,
                    "request_type": "general"
                })
                
                if "error" not in response:
                    result = response.get("result", "No response")
                    st.markdown(result)
                    st.session_state.messages.append({"role": "assistant", "content": result})
                else:
                    st.error(f"Error: {response['error']}")

def code_generation_page():
    """Code generation page"""
    st.header("💻 Code Generation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "Describe the code you want to generate:",
            height=100,
            placeholder="e.g., Create a Python function to calculate fibonacci numbers"
        )
        
        code_type = st.selectbox(
            "Code Type:",
            ["python", "javascript", "java", "c++", "general"]
        )
    
    with col2:
        st.markdown("**Options**")
        max_tokens = st.slider("Max Tokens", 100, 2000, 500)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    
    if st.button("Generate Code", type="primary"):
        if prompt:
            with st.spinner("Generating code..."):
                response = call_api("/code/generate", {
                    "prompt": prompt,
                    "code_type": code_type,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                })
                
                if "error" not in response:
                    result = response.get("result", "")
                    st.code(result, language=code_type)
                else:
                    st.error(f"Error: {response['error']}")
        else:
            st.warning("Please enter a prompt")

def research_page():
    """Research page"""
    st.header("🔍 Research")
    
    topic = st.text_input(
        "Research Topic:",
        placeholder="e.g., artificial intelligence trends 2024"
    )
    
    if st.button("Research Topic", type="primary"):
        if topic:
            with st.spinner("Researching..."):
                response = call_api("/research", {
                    "prompt": topic,
                    "request_type": "research"
                })
                
                if "error" not in response:
                    result = response.get("result", {})
                    
                    if isinstance(result, dict):
                        answer = result.get("answer", "No results found")
                        sources = result.get("sources", [])
                        
                        st.markdown("### Research Results")
                        st.markdown(answer)
                        
                        if sources:
                            st.markdown("### Sources")
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"{i}. {source}")
                    else:
                        st.markdown(result)
                else:
                    st.error(f"Error: {response['error']}")
        else:
            st.warning("Please enter a research topic")

def health_status_page():
    """Health status page"""
    st.header("🏥 System Health")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Health Check")
        if st.button("Check Health"):
            with st.spinner("Checking health..."):
                response = call_api("/health")
                
                if "error" not in response:
                    status = response.get("status", "unknown")
                    if status == "healthy":
                        st.success("✅ System is healthy")
                    else:
                        st.warning(f"⚠️ System status: {status}")
                    
                    st.json(response)
                else:
                    st.error(f"Error: {response['error']}")
    
    with col2:
        st.subheader("Detailed Health Check")
        if st.button("Detailed Check"):
            with st.spinner("Running detailed check..."):
                response = call_api("/health/detailed")
                
                if "error" not in response:
                    status = response.get("status", "unknown")
                    
                    if status == "healthy":
                        st.success("✅ All systems operational")
                    elif status == "degraded":
                        st.warning("⚠️ System degraded")
                    else:
                        st.error("❌ System unhealthy")
                    
                    # Display system resources
                    resources = response.get("system_resources", {})
                    if resources:
                        st.subheader("System Resources")
                        
                        cpu = resources.get("cpu_percent", 0)
                        memory = resources.get("memory", {})
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("CPU Usage", f"{cpu}%")
                        with col_b:
                            mem_percent = memory.get("percent", 0)
                            st.metric("Memory Usage", f"{mem_percent}%")
                    
                    st.json(response)
                else:
                    st.error(f"Error: {response['error']}")

if __name__ == "__main__":
    main()
