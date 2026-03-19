import sys
import json
import requests
from dataclasses import dataclass

import streamlit as st

from affiliate_mktg.src.search.search_index_manager import SearchIndexManager
from affiliate_mktg.src.core.models import SearchIndex, SearchInput
from affiliate_mktg.src.links.links_manager import LinksManager
from affiliate_mktg.src.core.enums import AvailabilityType
from affiliate_mktg.src.utils.logging_setup import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


@dataclass
class PostData:
    keywords: str
    selected_search_index: int
    entered_count: int
    selected_availability_type: str
    show_prime_delivery_items_only: bool
    show_isprimeexclusive_items_only: bool
    show_isbuyboxwinner_items_only: bool
    show_freeshipping_items_only: bool
    show_discount_items_only: bool
    entered_discount_percentage: int


@st.cache_resource
def get_search_index_manager():
    return SearchIndexManager("affiliate_mktg/src/search/search_index.json")


@st.cache_resource
def get_links_manager():
    return LinksManager()


@st.cache_data
def get_search_index_collection():
    searchIndexManager = get_search_index_manager()
    return searchIndexManager.generate_search_index()


class App:
    def __init__(self):
        logger.info("affiliate marketing streamlit app ...")
        self.searchIndexManager = get_search_index_manager()
        self.linksManager = get_links_manager()
        with st.expander("Versions Info", expanded=False):
            st.write(f"Running on Python version: {sys.version}")
            st.write(f"Streamlit version: {st.__version__}")

    def _fetch_session_stats(self):
        if "initial_call_done" not in st.session_state or not st.session_state.initial_call_done:
            session = requests.Session()
            STARLETTE_API_GET_STATS_URL = "http://localhost:8000/getstats"

            session_id = st.session_state.get("starlette_session_id", "")
            request_counts = st.session_state.get("starlette_session_data", {})
            request_counts_str = json.dumps(request_counts)
            cookies = {
                "session": session_id,
                "request_counts": request_counts_str,
            }

            response = session.get(STARLETTE_API_GET_STATS_URL, cookies=cookies)

            if response.ok:
                data = response.json()
                st.session_state["starlette_session_id"] = data.get("session_id")
                st.session_state["starlette_session_data"] = data.get("request_counts")
                st.session_state["initial_call_done"] = True
            else:
                st.error("Failed to fetch session data from Starlette.")

    def _render_stats_controls(self):
        st.write("Session ID:", st.session_state.get("starlette_session_id", "Not available"))
        session_data = st.session_state.get("starlette_session_data", {})
        if session_data:
            for date_str, count in session_data.items():
                st.write("Session Date:", date_str)
                st.write("Session Count:", str(count))

    def _post_generate_links_post_blogger(self, post_data: PostData):
        payload = {
            "src": {
                "keywords": post_data.keywords,
                "search_index": post_data.selected_search_index,
                "item_count": post_data.entered_count,
                "show_availability_type": post_data.selected_availability_type,
                "show_prime_delivery_items": post_data.show_prime_delivery_items_only,
                "show_isprimeexclusive_items": post_data.show_isprimeexclusive_items_only,
                "show_isbuyboxwinner_items": post_data.show_isbuyboxwinner_items_only,
                "show_freeshipping_items": post_data.show_freeshipping_items_only,
                "show_discount_items": post_data.show_discount_items_only,
                "discount_percentage": post_data.entered_discount_percentage,
            }
        }

        st.write(payload)

        STARLETTE_API_URL = "http://localhost:8000/run_generate_link_post_blog_manual"
        session = requests.Session()
        session_id = st.session_state.get("starlette_session_id", "")
        request_counts = st.session_state.get("starlette_session_data", {})
        request_counts_str = json.dumps(request_counts)
        cookies = {
            "session": session_id,
            "request_counts": request_counts_str,
        }

        response = session.post(
            STARLETTE_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            cookies=cookies,
        )

        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            success = result.get("success", False)
            content = result.get("content", "No content provided.")

            st.session_state["starlette_session_id"] = data.get("session_id")
            st.session_state["starlette_session_data"] = data.get("request_counts")

            st.session_state.show_error = not success
            if success:
                st.success(f"✅ {content}")
            else:
                st.error(f"❌ {content}")
            st.json(data)
        else:
            st.session_state.show_error = True
            response_status_code = response.status_code
            st.error(f"❌ Request failed with status code {response_status_code}")

    def _on_dropdown_change(self):
        st.session_state.checkbox_state_show_prime_delivery_items_only = False
        st.session_state.checkbox_state_show_isprimeexclusive_items_only = False
        st.session_state.checkbox_state_show_isbuyboxwinner_items_only = False
        st.session_state.checkbox_state_show_freeshipping_items_only = False
        st.session_state.checkbox_state_show_discount_items_only = False
        st.session_state.selected_state_selected_availability_type = "IN_STOCK"
        st.session_state.entered_count = 1

    def render(self):
        st.write("Hello from streamlit app!")

        self._fetch_session_stats()

        stats_placeholder = st.empty()
        with stats_placeholder.container():
            self._render_stats_controls()

        search_index_collection = get_search_index_collection()
        options_search_index = ["Select Search Index"] + [
            si.search_index for si in search_index_collection
        ]

        selected_search_index = st.selectbox(
            "Choose a search index option:",
            options_search_index,
            on_change=self._on_dropdown_change,
        )

        st.write("You selected search index :", selected_search_index)

        if selected_search_index and selected_search_index != "Select Search Index":
            found_search_index: SearchIndex = next(
                (
                    item
                    for item in search_index_collection
                    if item.search_index == selected_search_index
                ),
                None,
            )

            if found_search_index:
                st.session_state.button_disabled = True
                if selected_search_index != "All":
                    options_keyword = ["Select Keyword"] + found_search_index.keywords
                    selected_keyword = st.selectbox(
                        f"Select a keyword for {selected_search_index}",
                        options_keyword,
                    )
                    if selected_keyword and selected_keyword != "Select Keyword":
                        st.write("You selected keyword is :", selected_keyword)
                else:
                    selected_keyword = None

                entered_keyword = st.text_input("Enter a custom keyword", "")

                if entered_keyword:
                    st.write("You entered keyword :", entered_keyword)

                entered_count = st.number_input(
                    "Enter a count",
                    min_value=1,
                    max_value=10,
                    value=1,
                    step=1,
                    key="entered_count",
                )

                if entered_count:
                    st.write("You entered count :", entered_count)

                if selected_search_index != "All":
                    if (
                        (
                            (selected_keyword and selected_keyword != "Select Keyword")
                            or entered_keyword
                        )
                        and entered_count
                    ):
                        st.session_state.button_disabled = False
                else:
                    if entered_count:
                        st.session_state.button_disabled = False

                options_availability_type = [
                    availabilityType.value for availabilityType in AvailabilityType
                ]

                # selected_availability_type = st.selectbox(
                #     "Select a Availability Type",
                #     options_availability_type,
                #     key="selected_state_selected_availability_type",
                # )
                # if selected_availability_type:
                #     st.write(
                #         "You selected Availability Type is :",
                #         selected_availability_type,
                #     )

                selected_availability_type = st.multiselect(
                    "Select one or more Availability Type",
                    options_availability_type,
                    key="selected_state_selected_availability_type",
                )
                if selected_availability_type:
                    st.write(
                        "You selected Availability Types :",
                        selected_availability_type,
                    )

                if len(selected_availability_type) == 0:
                    st.session_state.button_disabled = True
                else:
                    st.session_state.button_disabled = False


                show_prime_delivery_items_only = st.checkbox(
                    "Show only Prime Delivery Items",
                    value=False,
                    key="checkbox_state_show_prime_delivery_items_only",
                )
                if show_prime_delivery_items_only:
                    st.write(
                        "You selected prime delivery items  :",
                        show_prime_delivery_items_only,
                    )

                if selected_search_index == "All":
                    show_isprimeexclusive_items_only = st.checkbox(
                        "Show only Prime Exclusive Items",
                        value=False,
                        key="checkbox_state_show_isprimeexclusive_items_only",
                    )
                    if show_isprimeexclusive_items_only:
                        st.write(
                            "You selected prime exclusive items  :",
                            show_isprimeexclusive_items_only,
                        )
                else:
                    show_isprimeexclusive_items_only = False

                show_isbuyboxwinner_items_only = st.checkbox(
                    "Show only Buy Box Winner Items",
                    value=False,
                    key="checkbox_state_show_isbuyboxwinner_items_only",
                )
                if show_isbuyboxwinner_items_only:
                    st.write(
                        "You selected buy box winner items  :",
                        show_isbuyboxwinner_items_only,
                    )

                show_freeshipping_items_only = st.checkbox(
                    "Show only Free Shipping Items",
                    value=False,
                    key="checkbox_state_show_freeshipping_items_only",
                )
                if show_freeshipping_items_only:
                    st.write(
                        "You selected free shipping items  :",
                        show_freeshipping_items_only,
                    )

                show_discount_items_only = st.checkbox(
                    "Show only Items with discount",
                    value=False,
                    key="checkbox_state_show_discount_items_only",
                )
                if show_discount_items_only:
                    st.write(
                        "You selected discount items  :",
                        show_discount_items_only,
                    )
                    entered_discount_percentage = st.number_input(
                        "Enter a minimum discuount percentage",
                        min_value=1,
                        max_value=100,
                        value=1,
                        step=1,
                    )
                    if entered_discount_percentage:
                        st.write(
                            "You entered discount percentage of :",
                            entered_discount_percentage,
                        )
                else:
                    entered_discount_percentage = 0

                keywords = ""
                if selected_search_index != "All":
                    keywords = (
                        entered_keyword if entered_keyword else selected_keyword
                    )
                else:
                    keywords = entered_keyword

                valid_keyword = keywords and keywords != "Select Keyword"
                valid_discount = (
                    show_discount_items_only and entered_discount_percentage
                )

                if valid_keyword and entered_count and valid_discount:
                    st.session_state.button_disabled = False

                st.subheader("Generate Links and Post to Blogger")
                button_clicked = st.button(
                    "Process Data",
                    disabled=st.session_state.button_disabled,
                    key="process_button",
                )
                if button_clicked:
                    with st.spinner("Generating and posting links..."):
                        post_data = PostData(
                            keywords=keywords,
                            selected_search_index=selected_search_index,
                            entered_count=entered_count,
                            selected_availability_type=selected_availability_type,
                            show_prime_delivery_items_only=show_prime_delivery_items_only,
                            show_isprimeexclusive_items_only=show_isprimeexclusive_items_only,
                            show_isbuyboxwinner_items_only=show_isbuyboxwinner_items_only,
                            show_freeshipping_items_only=show_freeshipping_items_only,
                            show_discount_items_only=show_discount_items_only,
                            entered_discount_percentage=entered_discount_percentage,
                        )

                        self._post_generate_links_post_blogger(post_data)
                        with stats_placeholder.container():
                            self._render_stats_controls()
                        st.session_state.initial_call_done = False


if __name__ == "__main__":
    myapp = App()
    myapp.render()
