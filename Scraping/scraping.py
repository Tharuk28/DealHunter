import requests
from bs4 import BeautifulSoup
import csv
import streamlit as st
import pandas as pd
st.image("D:\Tharuk\Deal Hunter\Scraping\WhatsApp Image 2024-11-18 at 14.08.49_ecc807e9.jpg", use_column_width=True)


st.markdown(
    """
    <style>
    .black-strip {
        background-color: black;
        color: white;
        padding: 20px;
        width: 100%;
        text-align: center;
        font-size: 50px; 
        font-weight: bold;
        border-radius: 2px;
        display: inline-block;
    }
    .stSelectbox label {
        background-color: black; 
        padding: 10px; 
        border-radius: 2px; 
        color: white; 
        font-size: 10px;
    }
    .stNumberInput label {
        background-color: black; 
        color: white; 
        padding: 10px;
        border-radius: 2px; 
        font-weight: bold; 
    }
    .stButton > button {
        background-color: black;
        color: white;
    }
    .stDownloadButton > button {
        background-color: black;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)




st.markdown('<div class="black-strip"> Deals Scraper </div>', unsafe_allow_html=True)
st.markdown(
    """
    <div style="background-color: skyblue; padding: 5px; border-radius: 2px; font-size: 4px; text-align: center;">
        <h3 style="color: black;">Choose a store and enter the page range </h3>
    </div>
    """,
    unsafe_allow_html=True,
)

store = ["All_store","Flipkart", "Amazon", "Paytm", "Foodpanda", "Freecharge", "Paytmmall"]
store_name = st.selectbox("Select Store", store)
start = st.number_input('Enter start page number:', min_value=1, step=1, value=1)

end =st.number_input('Enter end page number:', min_value=start, step=1, value=start)

csv_filename = "product_deals.csv"
submit_button = st.button("Submit")

if submit_button:
    try:
        if end > 1703:
            st.error("The DealsHeaven Website has only 1703 Pages.")
        else:
            with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Title", "Image", "Price", "Discount", "Special Price", "Link", "Rating"])

                for current_page in range(start, end + 1):
                    if store_name=="All_store":
                        url= f"https://dealsheaven.in/?page={current_page}"
                    else:
                        url = f"https://dealsheaven.in/store/{store_name.lower()}?page={current_page}"
                    response = requests.get(url)

                    if response.status_code != 200:
                        st.warning(f"Failed to retrieve page {current_page}. ")
                        continue

                    soup = BeautifulSoup(response.text, 'html.parser')
                    all_items = soup.find_all("div", class_="product-item-detail")

                    if not all_items:
                        st.warning(f"No products found on page {current_page}.")
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

                        writer.writerow([product.get('Title', 'N/A'), f'=HYPERLINK("{product.get("Image", "N/A")}","Image")', product.get('Price', 'N/A'), product.get('Discount', 'N/A'), product.get('Special Price', 'N/A'), f'=HYPERLINK("{product.get("Link", "N/A")}","Link")', product.get('Rating', 'N/A')])

            st.write("Data scraping and saving completed.")
            with open(csv_filename, "r", encoding="utf-8") as file:
                st.download_button(
                    label="Download CSV",
                    data=file,
                    file_name=csv_filename,
                    mime="text/csv"
                )

    except ValueError:
        st.error("Please enter valid integers for the starting and ending page.")