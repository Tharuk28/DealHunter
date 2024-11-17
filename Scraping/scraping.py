import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import plotly.express as px

# --- STORE NAMES ---
stores = ["Flipkart", "Amazon", "Paytm", "Foodpanda", "Freecharge", "Paytmmall"]

# --- SESSION STATE INITIALIZATION ---
if "scraped_data" not in st.session_state:
    st.session_state["scraped_data"] = pd.DataFrame()

if "selected_store" not in st.session_state:
    st.session_state["selected_store"] = None

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Scrape Data"  # Default page

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
if st.sidebar.button("Data Scraping"):
    st.session_state["current_page"] = "Scrape Data"

if st.sidebar.button("Dashboard"):
    st.session_state["current_page"] = "Dashboard"

if st.sidebar.button("About"):
    st.session_state["current_page"] = "About"

# --- SCRAPE DATA PAGE ---
if st.session_state["current_page"] == "Scrape Data":
    st.title("Deal Hunter")
    st.write("Choose a store and enter the page range you want to scrape")

    # Store selection and page input
    store_name = st.selectbox("Select Store", stores)
    start_page = st.text_input("Starting Page", "1")
    end_page = st.text_input("Ending Page", "1")

    if st.button("Scrape Data"):
        try:
            start = int(start_page)
            end = int(end_page)

            if start <= 0 or end <= 0:
                st.error("Page numbers must be greater than zero.")
            elif start > end:
                st.error("Starting page must be less than or equal to ending page.")
            elif end > 1703:
                st.error("The DealsHeaven Website has only 1703 Pages!")
            else:
                scraped_data = []
                for current_page in range(start, end + 1):
                    url = f"https://dealsheaven.in/store/{store_name.lower()}?page={current_page}"
                    response = requests.get(url)

                    if response.status_code != 200:
                        st.warning(f"Failed to retrieve page {current_page}. Skipping...")
                        continue

                    soup = BeautifulSoup(response.text, 'html.parser')
                    all_items = soup.find_all("div", class_="product-item-detail")

                    if not all_items:
                        st.warning(f"No products found on page {current_page}. Stopping scraper.")
                        break

                    for item in all_items:
                        product = {}

                        discount = item.find("div", class_="discount")
                        product['Discount'] = discount.text.strip() if discount else "N/A"

                        link = item.find("a", href=True)
                        product['Link'] = link['href'] if link else "N/A"

                        image = item.find("img", src=True)
                        product['Image'] = image['data-src'] if image else "N/A"

                        details_inner = item.find("div", class_="deatls-inner")

                        title = details_inner.find("h3", title=True) if details_inner else None
                        product['Title'] = title['title'].replace("[Apply coupon] ", "").replace('"', '') if title else "N/A"

                        price = details_inner.find("p", class_="price") if details_inner else None
                        product['Price'] = f"{price.text.strip().replace(',', '')}" if price else "N/A"

                        s_price = details_inner.find("p", class_="spacail-price") if details_inner else None
                        product['Special Price'] = f"{s_price.text.strip().replace(',', '')}" if s_price else "N/A"

                        rating = details_inner.find("div", class_="star-point") if details_inner else None
                        if rating:
                            style_width = rating.find("div", class_="star") if rating else None
                            if style_width:
                                percent = style_width.find("span", style=True) if style_width else None
                                if percent:
                                    style = percent['style']
                                    width_percentage = int(style.split(":")[1].replace('%', '').strip())
                                    stars = round((width_percentage / 100) * 5, 1)
                                    product['Rating'] = stars
                                else:
                                    product['Rating'] = "N/A"
                            else:
                                product['Rating'] = "N/A"
                        else:
                            product['Rating'] = "N/A"

                        scraped_data.append(product)

                # Save scraped data to session state
                st.session_state["scraped_data"] = pd.DataFrame(scraped_data)
                st.session_state["selected_store"] = store_name
                st.success("Data scraped successfully! Navigate to the Dashboard to view the results.")

        except ValueError:
            st.error("Please enter valid integers for the starting and ending page.")

# --- DASHBOARD PAGE ---
elif st.session_state["current_page"] == "Dashboard":
    st.title("Dashboard")
    if not st.session_state["scraped_data"].empty:
        data = st.session_state["scraped_data"]
        st.write("### Scraped Data Overview")
        st.dataframe(data)

        # Prepare data for pie chart
        discount_data = data["Discount"].value_counts().reset_index()
        discount_data.columns = ["Discount", "Count"]
        discount_data = discount_data[discount_data["Discount"] != "N/A"]

        if not discount_data.empty:
            # Pie chart
            st.write("### Discount Split")
            fig = px.pie(discount_data, values="Count", names="Discount", title="Discount Distribution")
            st.plotly_chart(fig)
        else:
            st.warning("No discount data available for visualization.")
    else:
        st.warning("No data available. Please scrape the data first.")

# --- ABOUT PAGE ---
elif st.session_state["current_page"] == "About":
    st.title("About")

    # Dynamic content based on selected store
    if st.session_state["selected_store"]:
        store = st.session_state["selected_store"]
        st.write(f"### About {store}")
        st.write(f"This application helps you scrape deals from **{store}** and visualize them in an interactive dashboard. Here, you can find discounts, special prices, and ratings of products on {store}.")
    else:
        st.write("### About Deal Hunter")
        st.write("Select a store from the Scrape Data page to view more about its deals and products.")
