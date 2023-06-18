import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st


def scrape_and_save(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error accessing the URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    book_items = soup.find_all('article', class_='product_pod')

    titles = []
    prices = []
    ratings = []
    availabilities = []
    descriptions = []

    for book in book_items:
        title = book.h3.a['title']
        titles.append(title)

        price = book.find('p', class_='price_color').text
        prices.append(price)

        rating = book.p['class'][-1]
        ratings.append(rating)

        availability = book.find('p', class_='instock availability').text.strip()
        availabilities.append(availability)

        book_url = book.h3.a['href']
        book_response = requests.get(f"http://books.toscrape.com/catalogue{book_url}")
        book_soup = BeautifulSoup(book_response.text, 'html.parser')
        try:
            description_element = book_soup.find('article', class_='product_page').find('p', recursive=False)
            description = description_element.text.strip()
        except AttributeError:
            description = "No description available"
        descriptions.append(description)

    data = {
        'Title': titles,
        'Price': prices,
        'Rating': ratings,
        'Availability': availabilities,
        'Description': descriptions
    }
    df = pd.DataFrame(data)

    # Apply custom CSS styles
    st.markdown(
        """
        <style>
        body {
            background-color: #ECC47D;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .dataframe {
            font-family: Arial, sans-serif;
            color: #333;
            border-collapse: collapse;
            width: 100%;
        }
        .dataframe th, .dataframe td {
            border: 1px solid #ddd;
            padding: 8px;
        }
        .dataframe th {
            background-color: #4CAF50;
            color: white;
        }
        .dataframe tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .dataframe tr:hover {
            background-color: #ddd;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    st.write("<h2 style='text-align: center;'>Book Details</h2>", unsafe_allow_html=True)
    st.dataframe(df.style.set_properties(**{'text-align': 'left'}))

    output_file = st.text_input("Enter output file name (e.g., book_details.xlsx):")
    if st.button("Save to Excel") and output_file:
        try:
            df.to_excel(output_file, index=False)
            st.success("Book details saved successfully.")
        except Exception as e:
            st.error(f"Error saving the file: {e}")


# Create the web UI using Streamlit
def main():
    st.set_page_config(page_title="Book Scraper", page_icon="📚")
    st.title("Book Scraper")

    url = st.text_input("Enter the URL", value="http://books.toscrape.com/catalogue/category/books/travel_2/index.html")
    if not url:
        st.warning("Please enter a URL.")
        st.stop()

    scrape_and_save(url)


if __name__ == "__main__":
    main()
