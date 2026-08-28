import streamlit as st

from ui_components import display_assistant_response


# ============================================================
# PAGE CONFIGURATION
# ============================================================
5
st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🤖 AI Document Assistant")
st.write("Ask questions about your documents.")


# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# MOCK LANGGRAPH RESPONSE
# ============================================================
# This is only for independent UI testing.
# Later, this function will be replaced by the actual
# LangGraph Supervisor connection.
# ============================================================

def get_mock_response(question):
    return {
        "answer": f"You asked: **{question}**",

        "sources": [
            {
                "document": "finance.pdf",
                "page": 1
            }
        ],

        "visuals": [],

        "route": [
            "Supervisor",
            "Search",
            "Final Response"
        ]
    }


# ============================================================
# DISPLAY PREVIOUS CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        # User message
        if message["role"] == "user":
            st.markdown(message["content"])

        # Assistant message
        elif message["role"] == "assistant":
            display_assistant_response(message)


# ============================================================
# USER INPUT
# ============================================================

prompt = st.chat_input(
    "Ask a question about your document..."
)


# ============================================================
# PROCESS USER QUESTION
# ============================================================

if prompt:

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    # --------------------------------------------------------
    # Get response
    # --------------------------------------------------------
    # Temporary mock response for independent testing.
    # --------------------------------------------------------

    result = get_mock_response(prompt)


    # --------------------------------------------------------
    # Display assistant response
    # --------------------------------------------------------

    with st.chat_message("assistant"):
        display_assistant_response(result)


    # --------------------------------------------------------
    # Save assistant response to chat history
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "answer": result["answer"],
            "sources": result["sources"],
            "visuals": result["visuals"],
            "route": result["route"]
        }
    )