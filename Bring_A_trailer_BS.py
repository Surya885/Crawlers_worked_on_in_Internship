import json
import requests
from bs4 import BeautifulSoup

data = []

# asset_url = "https://bringatrailer.com/listing/1969-ford-mustang-112/"
# asset_url = "https://bringatrailer.com/listing/2011-ferrari-599-gto-8/"
# asset_url = "https://bringatrailer.com/listing/1970-porsche-911t-coupe-38/"
asset_url = "https://bringatrailer.com/listing/1966-volvo-122s-42/"
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10 mmko-=-pokm -0oki9jn.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
r = requests.get(url=asset_url, headers=headers)
# print(r.content)
soup = BeautifulSoup(r.content, "html5lib")
# print(soup.prettify())

# url = "https://bringatrailer.com/auctions/"
# # auction_resp = requests.get(url)
# # print(auction_resp)

auction_description = soup.find(class_="post-excerpt").text
auction_description = " ".join(auction_description.split())
# print(auction_description)


auction_bid = soup.find(class_="listing-stats").text
auction_bid = " ".join(auction_bid.split())
print("auction_bid",auction_bid)
if "by" in auction_bid:
    status = "Sold"
    offering_result = "Offering_Closed"
else:
    status = "Unsold"
    offering_result = "Offering_Open"


auction_title = soup.find("div", class_="listing").find(class_="listing-sticky").find(class_="column") \
    .find(class_="post-title listing-post-title").text
auction_title = auction_title.split()[1]
# print(auction_title)


# auction_lotid = soup.find(class_="essentials").findAll("strong")
# print(auction_lotid)

auction_listing_details = soup.find(class_="column column-right column-right-force").find(class_="essentials") \
    .find("ul").text
auction_listing_details = (auction_listing_details.split())
# print(auction_listing_details)


auction_media = soup.find(class_="post-excerpt").find_all("img")
# print(auction_media)

image_list = []
for images in auction_media:
    image = (images["src"])
    # print(image)
    # imageUrl = "https://d2tt46f3mh26nl.cloudfront.net/" + images +"@3x"
    imageUrl = {
        "media_type": "image",
        "media_src": image,
        "thumbnail": None,
        "caption": None,
        "is_active": True
    }
    image_list.append(imageUrl)
    # print(image_list)

auction_bid_count = soup.find(class_="listing-stats-value number-bids-value").text
# print(auction_bid_count)

table = soup.find("table", {"class": "listing-stats"})
# print(table)
if table is not None:
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
        # print(data)

auction_end_date = data[2][1]
# print(auction_end_date)

auction_price = data[0][1]
auction_price = "".join(auction_price.replace("$", "").replace(",", "")).split()[1]
# print(auction_price)

auction_winning_bid = soup.find("div",class_="listing").find(class_="listing-sticky").find(class_="listing-intro")\
    .find(class_="listing-available").find(class_="listing-available-info").find(class_="info-value").text
# print(auction_winning_bid)



asset = {
    "platform_asset_id": "asset_id",
    "asset_type": "COLLECTIBLE",
    "pricing_type": "auction",
    "name": auction_title,
    "description": auction_description,
    "url": "each_asset_link",
    "tags": None,
    "symbol": None,
    "current_bid": "auction_price",
    "attributes": {"listing_details": auction_listing_details},
    "currency_code": "USD",
    "status": status,
    "auction_start": None,
    "auction_end": auction_end_date + " EST",
    "base_price": None,
    "bid_increment": None,
    "lot_id": None,
    "lot_name": None,
    "auction_id": None,
    "auction_name": None,
    "auction_type": None,
    "media": image_list,
    "custom_data": None,
    "reserve_price": None,
    "winning_bid":auction_winning_bid ,
    "final_price": "final_price",
    "offering_result": offering_result,
    "bid_count": auction_bid_count,
    "latest_bid": auction_price
}

print(json.dumps(asset))
