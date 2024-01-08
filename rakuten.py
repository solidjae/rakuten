import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from googletrans import Translator


def get_product_data(url):
    url = 'https://search.rakuten.co.jp/search/mall/%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB/'

    response = requests.get(url)

    product_data = []  # List to hold extracted product data

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the <script> tag containing 'window.__INITIAL_STATE__'
        script_tag = soup.find(lambda tag: tag.name == "script" and "window.__INITIAL_STATE__" in tag.text)

        if script_tag:
            script_content = script_tag.text

            json_str_start = script_content.find('window.__INITIAL_STATE__ = ') + len('window.__INITIAL_STATE__ = ')
            json_str_end = script_content.find('};', json_str_start) + 1
            if json_str_end == -1:
                json_str_end = len(script_content)
            json_str = script_content[json_str_start:json_str_end]

            try:
                data = json.loads(json_str)
                items = data['state']['data']['ichibaSearch']['items']

                for item in items:
                    name = item.get('name', 'No Name')
                    price = item.get('price', 'No Price')
                    review = item.get('review', {})
                    num_reviews = review.get('numReviews', 'No Reviews')

                    product_data.append({'Name': name, 'Price': price, 'Number of Reviews': num_reviews})

            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
            except KeyError as e:
                print(f"Key error: {e} - Check the JSON structure or the keys used")
        else:
            print("Script tag with 'window.__INITIAL_STATE__' not found")
    else:
        print('Request failed with status code', response.status_code)

    # Create DataFrame from the extracted product data
    df = pd.DataFrame(product_data)

    # Convert 'Price' and 'Number of Reviews' to numeric types
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Number of Reviews'] = pd.to_numeric(df['Number of Reviews'], errors='coerce')

    # Create a new column 'ReviewPriceProduct' as the product of 'Price' and 'Number of Reviews'
    df['ReviewPriceProduct'] = df['Price'] * df['Number of Reviews']

    # Display the updated DataFrame
    print(df)
    print(df['ReviewPriceProduct'].sum())
    df.to_csv('rakuten.csv', index=False)

def loop_through_keywords():
    translator = Translator()
    keywords = ["책상", "식탁", "책장", "선반", "행거", "의자"]
    trans_keywords = []
    for keyword in keywords:
        text = keyword
        src_language = 'ko'
        dest_language = 'ja'
        translation = translator.translate(text, src=src_language, dest=dest_language)
        trans_keywords.append(translation.text)
    
