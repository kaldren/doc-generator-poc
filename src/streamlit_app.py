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
st.markdown("Produce Conversion Design Document (CDD) using AI-powered agent.")

# Create two columns for the main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Configuration")
    
    # Input fields
    with st.form("erp_config_form"):
        source_erp = st.text_input(
            "Source ERP System",
            value="Alpha ERP",
            placeholder="We only support Alpha ERP for now. LOL!",
            help="Enter the name of the source ERP system"
        )
        
        target_erp = st.text_input(
            "Target ERP System", 
            value="Beta ERP",
            placeholder="We only support Beta ERP for now. LOL!",
            help="Enter the name of the target ERP system"
        )
        
        additional_context = st.text_area(
            "Strategy Document",
            value="""
                Strategy Document – Alpha ERP to Beta ERP Supplier Contact Data Conversion

                As part of our ERP migration initiative, we are transitioning supplier contact records from the legacy Alpha ERP system to the Beta ERP platform. The current dataset includes supplier names, contact details, and unique identifiers that are critical for procurement, compliance tracking, and audit readiness.

                The goal of this conversion is to:
                - Preserve data integrity during field transformations.
                - Comply with Beta ERP's formatting standards (e.g., E.164 for phone numbers).
                - Normalize inconsistent fields from Alpha ERP (e.g., upper/lower case, name concatenation).
                - Minimize post-conversion manual cleanup.

                Specific considerations:
                - All `CustomerID`s from Alpha must be transformed into Beta's `AccountNumber` format using the rule: `"CUST-" + CustomerID`, capped at 20 characters.
                - Contact names in Alpha are stored in `FirstName` and `LastName` and must be merged into `ContactName` in Beta.
                - Emails should be converted to lowercase to align with Beta's normalization policy.
                - Phone numbers need to be re-formatted to E.164 standard where possible.

                Please process the following dataset and convert it into Beta ERP’s expected format using the above transformation logic.

                ---

                Convert the following Alpha ERP data into the Beta ERP format.
                Follow these rules from the target ERP:

                CustomerID, SupplierName, FirstName, LastName, Email, Phone
                10001, Contoso Inc., John, Smith, John@Contoso.com, (206) 555-1234
                10002, Fabrikam LLC, Alice, Johnson, Alice@Fabrikam.com, 555-678-9012
                10003, Tailspin Toys, Bob, Adams, Bob@Tailspin.com, +1 800 555 0199
                10001, Contoso Inc., John, Smith, John@Contoso.com, (206) 555-1234
                10002, Fabrikam LLC, Alice, Johnson, Alice@Fabrikam.com, 555-678-9012
                10003, Tailspin Toys, Bob, Adams, Bob@Tailspin.com, +1 800 555 0199
                10004, Northwind Traders, Emily, Clark, Emily@Northwind.com, 404-555-7788
                10005, Adventure Works, Michael, Brown, Mike@Adventure.com, +1 (408) 555-1212
                10006, Alpine Ski House, Sarah, Thompson, sarah@alpine.com, (512) 999-0000
                10007, Blue Yonder, David, Lee, dlee@blueyonder.com, 212-333-4567
                10008, Proseware Inc., Laura, Martinez, laura@proseware.com, +44 20 7946 0958
                10009, Litware, Steve, Wilson, swilson@litware.com, 7135550101
                10010, Wide World Importers, Rachel, Green, rachel.green@importers.com, (503) 321-0001
                10011, Southridge Video, Tom, Hardy, tom.hardy@southridge.com, 999-888-7777
                10012, Coho Winery, Olivia, Davis, olivia@cohowines.com, 800-222-3333
            """,
            placeholder="Paste the strategy document here.",
            height=150,
            help="A strategy document is a document that outlines the strategy for the ERP conversion."
        )
        
        submit_config = st.form_submit_button("Generate CDD", type="primary")
    
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
    st.header("CDD Generation")
    
    if not st.session_state.agent_initialized:
        st.info("Fill in the configuration and click 'Generate CDD' to start the generation.")
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
    2. Paste the strategy document that outlines the strategy for the ERP conversion.
    3. Click "Generate CDD"
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

    st.header("🗄️ Data")
    st.write("See the data that was ingested into Azure AI Search.")
    if st.button("Show Ingested Data"):
        st.switch_page("pages/ingested-data.py")

# Cleanup function (called when app closes)
if st.session_state.agent_initialized and st.session_state.cdd_agent:
    # Note: Streamlit doesn't have a built-in cleanup mechanism
    # In a production app, you might want to implement proper cleanup
    pass 