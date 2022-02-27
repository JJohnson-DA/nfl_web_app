"""
Frameworks for running multiple Streamlit applications as a single app.
"""
import streamlit as st


class MultiPage:
    """Framework for combining multiple streamlit applications.
    Usage:
        keep each page in a separate file.
        import page1
        import page2
        app = MultiPage()
        app.add_page("Foo", page1.app)
        app.add_page("Bar", page2.app)
        app.run()
    """

    def __init__(self):
        self.apps = []

    def add_page(self, title, func):
        """Adds a new page.
        Parameters
        ----------
        func:
            the python function to render this page.
        title:
            title of the page. Appears in the dropdown in the sidebar.
        """
        self.apps.append({"title": title, "function": func})

    def run(self):
        with st.sidebar:
            app = st.selectbox(
                label="Navigation",
                options=self.apps,
                format_func=lambda app: app["title"],
            )
            st.write("---")

        app["function"]()

