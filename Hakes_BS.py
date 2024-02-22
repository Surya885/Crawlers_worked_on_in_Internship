from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json


def website_parser(asset_url):
    asset_link = "https://www.hakes.com/Auction/ItemDetail/268175/LINCOLN-WASHINGTON-19TH-CENTURY-US-MINT-MEDALS-IN-SILVER-AND-BRASS-W-B-P-ON-TRUNCATIONS"  #auction ended
    # asset_link = "https://www.hakes.com/Auction/ItemDetail/267608/DECLARATION-OF-INDEPENDENCE-SCARCE-ELEAZER-HUNTINGTON-PRINTING-C-1820-1825"  #Auction not ended
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10 mmko-=-pokm -0oki9jn.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    r = requests.get(url=asset_link, headers=headers)
    # print(r.content)
    soup = BeautifulSoup(r.content, "html5lib")
    # print(soup.prettify())

    book_currentbid = soup.find("div", id="ContentArea", class_="container") \
        .find("div", id="ContentAreaMain").find("div", id="ItemDetailContainer", class_="AuctionItemDetailContainer") \
        .find("div", id="ItemBidDetail", class_="ItemDetailItem").find("div", class_="SmallDetailsCollection").find(
        "div", class_="DetailItem") \
        .find("div", class_="Value").text
    book_currentbid = book_currentbid.replace("$", "").replace(",", "")
    # print(book_currentbid.strip())

    book_enddate = soup.find("div", id="ContentArea", class_="container") \
        .find("div", id="ContentAreaMain").find("div", id="ItemDetailContainer", class_="AuctionItemDetailContainer") \
        .find("div", id="ItemBidDetail", class_="ItemDetailItem").find("div", class_="SmallDetailsCollection") \
        .find("div", class_="DetailItem medium-text").find("div", class_="Value", id="ScheduledCloseDateTime").text
    book_enddate = (book_enddate[0:40])
    bookend = book_enddate.strip()
    print(bookend)
    data_obj = datetime.strptime(bookend, "%A, %B %d, %Y %I:%M:%S %p")
    # print(data_obj)

    book_description = soup.find("div", id="ContentArea", class_="container") \
        .find("div", id="ContentAreaMain").find("div", id="ItemDetailContainer", class_="AuctionItemDetailContainer") \
        .find("div", class_="ItemDescription").text
    book_description = " ".join(book_description.strip().split())
    # print(book_description.strip())

    book_name = soup.find("div", id="ContentArea", class_="container") \
        .find("div", id="ContentAreaMain").find("div", id="ItemDetailContainer", class_="AuctionItemDetailContainer") \
        .find("div", class_="Title").text
    # print(book_name.strip())

    book_lotid = asset_link.split("/")
    book_lotid = (book_lotid[5])
    # print(book_lotid)

    book_auctionid = soup.find("div", id="ContentArea", class_="container") \
        .find("div", id="ContentAreaMain").find("div", id="ItemDetailContainer", class_="AuctionItemDetailContainer") \
        .find("div", class_="ItemActionContainer").find("div", class_="ItemBreadcrumb").text
    book_auctionid = "".join(book_auctionid.strip().split())
    # print(book_auctionid)

    book_infobid = {}
    book_bid = soup.findAll("div", class_="DetailItem")
    # print(book_bid)
    for each_key in book_bid:
        book_key = each_key.find("div", class_="Label").text
        book_key = (book_key.replace(":", "").strip())
        # print(book_key)
        book_value = each_key.find("div", class_="Value").text
        book_value = (book_value.strip())
        # print(book_value)
        # print(book_key+"  "+book_value)

        book_infobid[book_key] = book_value
    print(book_infobid)
    bookbidcount = (book_infobid["Bids"])
    print(bookbidcount)

    if "Bidding Ended" in book_infobid:
        status = "Sold"
        offering_result = "Unavailable"
    else:
        status = "Unsold"
        offering_result = "Available"

    book_picture = soup.find("div", id="ContentArea", class_="container") \
        .find("div", id="ContentAreaMain").find("div", id="ItemDetailContainer", class_="AuctionItemDetailContainer") \
        .find("div", class_="photoset-grid-lightbox").findAll("img")
    # print(book_picture)
    allasset = []
    images = []
    for image in book_picture:

        # print(image["data-highres"])
        image = "https://www.hakes.com/" + image["data-highres"]
        # print(image)
        imageUrl = {
            "media_type": "image",
            "media_src": image,
            "thumbnail": None,
            "caption": None,
            "is_active": True
        }
        images.append(imageUrl)

        asset = {
            "platform_asset_id": book_lotid,
            "asset_type": "COLLECTIBLE",
            "pricing_type": "auction",
            "name": book_name,
            "description": book_description,
            "url": asset_url,
            "tags": None,
            "symbol": None,
            "current_bid": book_currentbid,
            "attributes": {"asset_year": None,
                           "asset_specialist": None,
                           "asset_artist": None},
            "currency_code": "USD",
            "status": status,
            "auction_start": None,
            "auction_end": str(data_obj) + " EST",
            "base_price": None,
            "bid_increment": None,
            "lot_id": None,
            "lot_name": None,
            "auction_id": book_auctionid,
            "auction_name": None,
            "auction_type": None,
            "media": images,
            "custom_data": {"brand_name": None},
            "reserve_price": None,
            "winning_bid": book_currentbid,
            "final_price": None,
            "offering_result": offering_result,
            "latest_bid": None,
            "bid_count": bookbidcount
        }
    # print(json.dumps(asset))
    allasset.append(asset)
    print(json.dumps(allasset))


if __name__ == "__main__":
    website_parser(asset_url="https://www.hakes.com/Auction/ItemDetail/268175/LINCOLN-WASHINGTON-19TH-CENTURY-US-MINT-MEDALS-IN-SILVER-AND-BRASS-W-B-P-ON-TRUNCATIONS")
