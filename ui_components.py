import streamlit as st


def display_sources(sources):
    """Display document and page references."""

    if not sources:
        return

    st.markdown("#### 📚 Sources")

    for source in sources:
        document = source.get("document", "Unknown document")
        page = source.get("page", "Unknown")

        st.write(f"📄 {document} — Page {page}")


def display_execution_status(route):
    """Display agent execution route without exposing chain-of-thought."""

    if not route:
        return

    st.markdown("#### 🔄 Execution Status")

    st.write(" → ".join(route))


def display_visuals(visuals):
    """Display referenced images or charts."""

    if not visuals:
        return

    st.markdown("#### 🖼️ Referenced Visuals")

    for visual in visuals:

        # Support a simple image path or URL
        if isinstance(visual, str):
            st.image(visual)

        # Support visual information returned as a dictionary
        elif isinstance(visual, dict):

            image = visual.get("image")
            page = visual.get("page")
            caption = visual.get("caption")

            if image:
                if caption and page:
                    st.image(
                        image,
                        caption=f"{caption} — Page {page}"
                    )
                elif page:
                    st.image(
                        image,
                        caption=f"Page {page}"
                    )
                elif caption:
                    st.image(
                        image,
                        caption=caption
                    )
                else:
                    st.image(image)


def display_assistant_response(response):
    """Display final answer and related information."""

    st.markdown(
        response.get("answer", "")
    )

    display_sources(
        response.get("sources", [])
    )

    display_execution_status(
        response.get("route", [])
    )

    display_visuals(
        response.get("visuals", [])
    )
