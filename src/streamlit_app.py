import streamlit as st
import asyncio
import os
import dotenv
from agents.CddAgent import CddAgent

dotenv.load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CDD Agent Demo",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'cdd_agent' not in st.session_state:
    st.session_state.cdd_agent = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False

st.title("CDD Agent Demo")
st.markdown("Convert data between ERP systems using AI-powered CDD analysis")

# Create two columns for the main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Configuration")
    
    # Input fields
    with st.form("erp_config_form"):
        source_erp = st.text_input(
            "Source ERP System",
            placeholder="e.g., Alpha ERP",
            help="Enter the name of the source ERP system"
        )
        
        target_erp = st.text_input(
            "Target ERP System", 
            placeholder="e.g., Beta ERP",
            help="Enter the name of the target ERP system"
        )
        
        additional_context = st.text_area(
            "Additional Context",
            placeholder="Enter CSV data, field mappings, or other relevant information...",
            height=150,
            help="Provide additional context like CSV data, field descriptions, or specific migration requirements"
        )
        
        submit_config = st.form_submit_button("Initialize CDD Agent", type="primary")
    
    # Initialize agent when form is submitted
    if submit_config and source_erp and target_erp:
        with st.spinner("Initializing CDD Agent..."):
            try:
                # Create new CDD agent
                st.session_state.cdd_agent = CddAgent(
                    source_erp=source_erp,
                    target_erp=target_erp,
                    additional_context=additional_context
                )
                st.session_state.agent_initialized = True
                st.session_state.chat_history = []  # Reset chat history
                
                # Send additional context as the first message if provided
                if additional_context.strip():
                    context_message = f"Here is the additional context for this ERP conversion:\n\n{additional_context}"
                    
                    # Add user message to chat history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": context_message
                    })
                    
                    # Process the context with the agent and get response
                    try:
                        async def process_initial_context():
                            response = await st.session_state.cdd_agent.process_query(context_message)
                            return response
                        
                        initial_response = asyncio.run(process_initial_context())
                        
                        # Add agent response to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": initial_response
                        })
                        
                    except Exception as e:
                        error_msg = f"❌ Error processing initial context: {str(e)}"
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                
                st.success(f"✅ CDD Agent initialized for {source_erp} → {target_erp}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to initialize agent: {str(e)}")
    
    elif submit_config:
        st.warning("⚠️ Please fill in both Source and Target ERP systems")
    
    # Display current configuration
    if st.session_state.agent_initialized and st.session_state.cdd_agent:
        st.info(f"**Current Configuration:**\n\n"
                f"📥 Source: {st.session_state.cdd_agent.source_erp}\n\n"
                f"📤 Target: {st.session_state.cdd_agent.target_erp}")

with col2:
    st.header("Chat Interface")
    
    if not st.session_state.agent_initialized:
        st.info("👈 Please configure and initialize the CDD Agent first")
    else:
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(message["content"])
        
        # Chat input
        user_query = st.chat_input("Ask about ERP data conversion...")
        
        if user_query:
            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_query
            })
            
            # Display user message immediately
            with st.chat_message("user"):
                st.write(user_query)
            
            # Process query with CDD agent
            with st.chat_message("assistant"):
                with st.spinner("Processing query..."):
                    try:
                        # Run async function
                        async def process_query():
                            response = await st.session_state.cdd_agent.process_query(user_query)
                            return response
                        
                        # Use asyncio to run the async function
                        response = asyncio.run(process_query())
                        
                        # Display response
                        st.write(response)
                        
                        # Add assistant response to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": response
                        })
                        
                    except Exception as e:
                        error_msg = f"❌ Error processing query: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": error_msg
                        })

# Sidebar with helpful information
with st.sidebar:
    st.header("💡 Tips")
    st.markdown("""
    **Getting Started:**
    1. Enter your source and target ERP systems
    2. Add any relevant context (CSV data, mappings, etc.)
    3. Click "Initialize CDD Agent"
    4. Start asking questions about data conversion
    
    **Example Questions:**
    - "How do I map customer data from Alpha to Beta?"
    - "What are the field differences between these systems?"
    - "Help me convert this CSV data structure"
    - "Are there any data quality issues I should watch for?"
    """)
    
    st.header("🔧 Environment")
    required_vars = [
        "AZURE_OPENAI_CHAT_MODEL_ID",
        "AZURE_OPENAI_API_KEY", 
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_SEARCH_SERVICE_ENDPOINT",
        "AZURE_SEARCH_INDEX_NAME",
        "AZURE_SEARCH_API_KEY"
    ]
    
    for var in required_vars:
        if os.getenv(var):
            st.success(f"✅ {var}")
        else:
            st.error(f"❌ {var}")

# Cleanup function (called when app closes)
if st.session_state.agent_initialized and st.session_state.cdd_agent:
    # Note: Streamlit doesn't have a built-in cleanup mechanism
    # In a production app, you might want to implement proper cleanup
    pass 