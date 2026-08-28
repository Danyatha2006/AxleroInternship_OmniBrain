import streamlit as st

from ui_components import display_assistant_response
from orchestrator.graph import app


# ============================================================
# PAGE CONFIGURATION
# ============================================================

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
# DISPLAY PREVIOUS CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["role"] == "user":
            st.markdown(message["content"])

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
    # CALL LANGGRAPH SUPERVISOR
    # --------------------------------------------------------

    try:

        result = app.invoke(
            {
                "query": prompt
            }
        )


        # ----------------------------------------------------
        # Convert LangGraph result into UI format
        # ----------------------------------------------------

        ui_result = {
            "answer": result.get(
                "final_response",
                "No response was generated."
            ),

            "sources": result.get(
                "sources",
                []
            ),

            "visuals": result.get(
                "visuals",
                []
            ),

            "route": [
                "Supervisor",
                result.get(
                    "selected_agent",
                    "Unknown"
                ),
                "Final Response"
            ]
        }


        # ----------------------------------------------------
        # Display assistant response
        # ----------------------------------------------------

        with st.chat_message("assistant"):
            display_assistant_response(ui_result)


        # ----------------------------------------------------
        # Save assistant response
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "answer": ui_result["answer"],
                "sources": ui_result["sources"],
                "visuals": ui_result["visuals"],
                "route": ui_result["route"]
            }
        )


    except Exception as error:

        # ----------------------------------------------------
        # Display error without exposing internal details
        # ----------------------------------------------------

        with st.chat_message("assistant"):
            st.error(
                "Sorry, I could not process your question."
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "answer": (
                    "Sorry, I could not process "
                    "your question."
                ),
                "sources": [],
                "visuals": [],
                "route": []
            }
        )

        st.write(
            "Please check the terminal for the "
            "technical error."
        )

