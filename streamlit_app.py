"""
Streamlit Client Application for FASTMCP Sales ERP.
Provides Manager and Executive dashboards with NLP chat interface.
"""
import streamlit as st
import requests
import json
from datetime import datetime, date, timedelta
import pandas as pd
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "http://localhost:8000"
PAGE_ICON = "📊"
LAYOUT = "wide"

# Page config
st.set_page_config(
    page_title="FASTMCP – Sales ERP",
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# Session State Management
# ============================================================================

def initialize_session():
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = 1
    if "user_role" not in st.session_state:
        st.session_state.user_role = "manager"
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []


# ============================================================================
# API Helper Functions
# ============================================================================

def api_call(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make an API call to the FastAPI backend."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"success": False, "error": f"Unknown method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to API server. Is it running on port 8000?"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "API request timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_manager_dashboard(manager_id: int) -> Dict[str, Any]:
    """Fetch manager dashboard data."""
    return api_call(f"/api/manager/dashboard/{manager_id}")


def get_executive_dashboard(executive_id: int) -> Dict[str, Any]:
    """Fetch executive dashboard data."""
    return api_call(f"/api/executive/dashboard/{executive_id}")


def process_nlp_message(message: str, user_id: int) -> Dict[str, Any]:
    """Send a message to the NLP processor."""
    return api_call("/api/mcp/message", method="POST", data={
        "message": message,
        "user_id": user_id,
    })


def get_users() -> Dict[str, Any]:
    """Fetch all users."""
    return api_call("/api/users")


# ============================================================================
# Dashboard Components
# ============================================================================

def display_metrics(statistics: Dict[str, Any]):
    """Display key metrics in columns."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Projects",
            statistics.get("total_projects", 0),
            delta=None,
        )
    
    with col2:
        st.metric(
            "Active Projects",
            statistics.get("active_projects", 0),
            delta=None,
        )
    
    with col3:
        st.metric(
            "Total Revenue",
            f"₹{statistics.get('total_revenue', 0):,.0f}",
            delta=None,
        )
    
    with col4:
        st.metric(
            "Pending Payments",
            statistics.get("pending_payments_count", 0),
            delta=None,
        )


def display_projects_table(projects: list):
    """Display projects in a table."""
    if not projects:
        st.info("No projects found")
        return
    
    # Convert to DataFrame for better display
    df = pd.DataFrame([
        {
            "Project": p.get("name", "N/A"),
            "Client": p.get("client", "N/A"),
            "Status": p.get("status", "N/A").upper(),
            "Value": f"₹{p.get('estimated_value', 0):,.0f}" if p.get('estimated_value') else "N/A",
        }
        for p in projects
    ])
    
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_manager_dashboard():
    """Display the Manager Dashboard."""
    st.title("👔 Manager Dashboard")
    
    # Fetch data
    result = get_manager_dashboard(st.session_state.user_id)
    
    if not result.get("success"):
        st.error(f"Error loading dashboard: {result.get('error', 'Unknown error')}")
        return
    
    # Display metrics
    st.subheader("📊 Key Metrics")
    display_metrics(result.get("statistics", {}))
    
    # Display projects
    st.subheader("📁 All Projects")
    display_projects_table(result.get("projects", []))
    
    # Display statistics
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💰 Revenue Summary")
        stats = result.get("statistics", {})
        st.write(f"""
        - **Total Revenue**: ₹{stats.get('total_revenue', 0):,.0f}
        - **Active Projects**: {stats.get('active_projects', 0)}
        - **Total Projects**: {stats.get('total_projects', 0)}
        """)
    
    with col2:
        st.subheader("⚠️ Pending Items")
        stats = result.get("statistics", {})
        st.write(f"""
        - **Pending Payments**: {stats.get('pending_payments_count', 0)}
        """)


def display_executive_dashboard():
    """Display the Executive Dashboard."""
    st.title("👤 Executive Dashboard")
    
    # Fetch data
    result = get_executive_dashboard(st.session_state.user_id)
    
    if not result.get("success"):
        st.error(f"Error loading dashboard: {result.get('error', 'Unknown error')}")
        return
    
    # Display metrics
    st.subheader("📊 Your Projects")
    display_metrics(result.get("statistics", {}))
    
    # Display projects
    st.subheader("📁 My Projects")
    display_projects_table(result.get("projects", []))


# ============================================================================
# NLP Chat Interface
# ============================================================================

def display_nlp_chat():
    """Display the NLP chat interface."""
    st.title("💬 NLP Message Processor")
    
    st.write("""
    Send natural language messages to automate sales operations.
    Examples:
    - "Google ka iss week ka 1.2 lakh payment aa gaya"
    - "Ramesh is assigned to Google project"
    - "Google project active karo"
    - "Dharmendra ke sare active project dikhado"
    """)
    
    # Message input
    col1, col2 = st.columns([4, 1])
    with col1:
        message = st.text_input(
            "Enter your message:",
            placeholder="e.g., Google ka iss week ka 1.2 lakh payment aa gaya",
            label_visibility="collapsed",
        )
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Process message
    if send_button and message:
        with st.spinner("Processing message..."):
            result = process_nlp_message(message, st.session_state.user_id)
        
        # Display result
        if result.get("success"):
            st.success("✅ Message processed successfully!")
            
            # Show parsed intent
            parsed = result.get("parsed", {})
            st.subheader("🔍 Parsed Intent")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Intent**: {parsed.get('intent', 'N/A')}")
            with col2:
                st.write(f"**Action**: {parsed.get('action', 'N/A')}")
            with col3:
                st.write(f"**Confidence**: {parsed.get('confidence', 0):.0%}")
            
            # Show extracted entities
            st.subheader("📋 Extracted Entities")
            entities = {k: v for k, v in parsed.items() 
                       if k not in ['intent', 'action', 'confidence', 'original_message', 'timestamp']}
            if entities:
                for key, value in entities.items():
                    st.write(f"- **{key.replace('_', ' ').title()}**: {value}")
            
            # Show execution result
            execution = result.get("execution", {})
            if execution.get("success"):
                st.subheader("✨ Execution Result")
                st.write(f"**Status**: {execution.get('action', 'N/A')}")
                data = execution.get("data", {})
                for key, value in data.items():
                    st.write(f"- **{key.replace('_', ' ').title()}**: {value}")
        else:
            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    # Display chat history
    st.subheader("📝 Message History")
    if st.session_state.chat_messages:
        for msg in st.session_state.chat_messages[-5:]:  # Show last 5 messages
            with st.expander(f"📨 {msg['message'][:50]}..."):
                st.write(msg)
    else:
        st.info("No messages yet. Send a message to get started!")


# ============================================================================
# Sidebar Navigation
# ============================================================================

def display_sidebar():
    """Display sidebar with navigation and settings."""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # User selection
        st.subheader("👤 User Profile")
        users_result = get_users()
        
        if users_result.get("success"):
            users = users_result.get("users", [])
            user_options = {u["id"]: f"{u['name']} ({u['role']})" for u in users}
            
            selected_user_id = st.selectbox(
                "Select User:",
                options=list(user_options.keys()),
                format_func=lambda x: user_options[x],
                index=0,
            )
            
            st.session_state.user_id = selected_user_id
            
            # Get user role
            selected_user = next((u for u in users if u["id"] == selected_user_id), None)
            if selected_user:
                st.session_state.user_role = selected_user["role"]
        else:
            st.error("Could not load users")
        
        st.divider()
        
        # Navigation
        st.subheader("📍 Navigation")
        page = st.radio(
            "Select Page:",
            options=["Dashboard", "NLP Chat", "About"],
            label_visibility="collapsed",
        )
        
        st.divider()
        
        # Server status
        st.subheader("🔗 Server Status")
        health = api_call("/health")
        if health.get("success") or "status" in health:
            st.success(f"✅ Connected (v{health.get('version', 'unknown')})")
        else:
            st.error("❌ Cannot connect to API server")
        
        st.divider()
        
        # About
        st.subheader("ℹ️ About")
        st.write("""
        **FASTMCP – Sales Team Automation ERP**
        
        Version: 1.0.0
        
        A comprehensive MCP server for managing sales teams, projects, employees, and payments.
        """)
        
        return page


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point."""
    initialize_session()
    
    page = display_sidebar()
    
    if page == "Dashboard":
        if st.session_state.user_role == "manager":
            display_manager_dashboard()
        else:
            display_executive_dashboard()
    
    elif page == "NLP Chat":
        display_nlp_chat()
    
    elif page == "About":
        st.title("📖 About FASTMCP")
        st.markdown("""
        ## FASTMCP – Sales Team Automation ERP
        
        FASTMCP is a comprehensive **MCP Server** built with **FastAPI**, **PostgreSQL**, 
        and **SQLAlchemy ORM** for automating sales team workflows.
        
        ### Key Features
        
        - **Sales Project Management** – Track multiple projects per client
        - **Team Management** – Assign employees to projects with duration tracking
        - **Payment Tracking** – Record and track weekly/pending payments
        - **NLP Automation** – Convert natural language messages into database actions
        - **Role-Based Dashboards** – Separate views for Managers and Executives
        
        ### Technology Stack
        
        - **Backend**: FastAPI + fastmcp
        - **Database**: PostgreSQL + SQLAlchemy ORM
        - **Frontend**: Streamlit (this app) + React
        - **Language**: Python 3.11+
        
        ### Example NLP Commands
        
        - "Google ka iss week ka 1.2 lakh payment aa gaya"
        - "Ramesh is assigned to Google project"
        - "Google project active karo"
        - "Dharmendra ke sare active project dikhado"
        
        ### Getting Started
        
        1. Ensure the FastAPI server is running on `http://localhost:8000`
        2. Select a user from the sidebar
        3. Navigate to Dashboard or NLP Chat
        4. Explore the features!
        
        ### Documentation
        
        For more information, see `FASTMCP_README.md` in the project root.
        """)


if __name__ == "__main__":
    main()
