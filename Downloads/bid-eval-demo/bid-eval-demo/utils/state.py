import streamlit as st
from typing import Dict, List, Any


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "tender_data" not in st.session_state:
        st.session_state.tender_data = None
    if "evaluation_criteria" not in st.session_state:
        st.session_state.evaluation_criteria = []
    if "supplier_evaluations" not in st.session_state:
        st.session_state.supplier_evaluations = []
    if "api_key" not in st.session_state:
        st.session_state.api_key = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def set_tender_data(data: Dict[str, Any]):
    """Store tender data in session state."""
    st.session_state.tender_data = data


def get_tender_data() -> Dict[str, Any]:
    """Retrieve tender data from session state."""
    return st.session_state.tender_data


def set_evaluation_criteria(criteria: List[Dict[str, Any]]):
    """Store evaluation criteria in session state."""
    st.session_state.evaluation_criteria = criteria


def get_evaluation_criteria() -> List[Dict[str, Any]]:
    """Retrieve evaluation criteria from session state."""
    return st.session_state.evaluation_criteria


def add_supplier_evaluation(evaluation: Dict[str, Any]):
    """Add a supplier evaluation to session state."""
    st.session_state.supplier_evaluations.append(evaluation)


def get_supplier_evaluations() -> List[Dict[str, Any]]:
    """Retrieve all supplier evaluations from session state."""
    return st.session_state.supplier_evaluations


def set_supplier_evaluations(evaluations: List[Dict[str, Any]]):
    """Replace all supplier evaluations in session state."""
    st.session_state.supplier_evaluations = evaluations


def clear_all_data():
    """Clear all stored data from session state."""
    st.session_state.tender_data = None
    st.session_state.evaluation_criteria = []
    st.session_state.supplier_evaluations = []
    st.session_state.chat_history = []


def add_chat_message(role: str, content: str):
    """Add a message to chat history."""
    st.session_state.chat_history.append({"role": role, "content": content})


def get_chat_history() -> List[Dict[str, str]]:
    """Retrieve chat history."""
    return st.session_state.chat_history


def set_api_key(api_key: str):
    """Store API key in session state."""
    st.session_state.api_key = api_key


def get_api_key() -> str:
    """Retrieve API key from session state."""
    return st.session_state.api_key
