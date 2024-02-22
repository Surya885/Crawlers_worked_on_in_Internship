import requests
import json
import datetime

import time
from calendar import timegm



def website_parser():

    try:
        url = "https://themarket.bonhams.com/en/ajax/latest-vehicles?direction=asc&type=auction&limit=10000"

        payload = {}
        headers = {
            'x-requested-with': 'XMLHttpRequest',
            'Cookie': 'AWSALB=4qK0u5HwCbMeGURs1kzmcVAj8Aa/1bkTGJph5CB1TuCxLUOKRC+gNmueu6J7kXypOyq/1J9BZL5BG+8IX2eOem2blo+QvjazQ0ejUNztCR9zHnJRfgmFSa2vabCO; AWSALBCORS=4qK0u5HwCbMeGURs1kzmcVAj8Aa/1bkTGJph5CB1TuCxLUOKRC+gNmueu6J7kXypOyq/1J9BZL5BG+8IX2eOem2blo+QvjazQ0ejUNztCR9zHnJRfgmFSa2vabCO; XSRF-TOKEN=oHZRRaCB13JGLMLgAiaulTtZF5EMrbhikysyx95j; laravel_session=6UMRjdhAoofIsmMFKD5Bo7mir4udmFQ0lSBIxwDv'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        json_data = json.loads(response.content)

    except Exception as e:
        print("error in auction parser :", e)



def asset_parser(asset_data):
    pc_id = None
    asset_id = None
    asset_name = None
    image_list = []
    status = None
    current = None
    offering_end = None
    offering_result = None
    environment = ["dev", "prod"]

    try:
        asset_id = asset_data["id"]
        asset_name = asset_data["url"].split("/")[-2]
        asset_description = asset_data["auction-footer"]
        asset_link = asset_data["url"]
        asset_brand = asset_data["make"]
        if asset_data["highest_bid"] is not None:
            current_bid = asset_data["highest_bid"] / 100
        else:
            current_bid = "0"
        currency_code = asset_data["currency"]

        if asset_data["status"] == "live":
            status = "OFFERING_OPEN"
        elif asset_data["status"] == "preview":
            status = "OFFERING_ANNOUNCED"
        elif asset_data["status"] == "buy-now":
            status = "OFFERING_OPEN"

        offering_start = datetime.datetime.strptime(asset_data["created-at"], "%d-%m-%Y %H:%M:%S")
        offering_end = datetime.datetime.strptime(asset_data["end-date"], "%d-%m-%Y %H:%M:%S")

        image = {
            "media_type": "image",
            "media_src": asset_data["image"],
            "thumbnail": None,
            "caption": None,
            "is_active": True
        }

        asset = {
            "platform_asset_id": asset_id,
            "asset_type": "COLLECTIBLE",
            "pricing_type": "auction",
            "name": asset_name,
            "description": asset_description,
            "url": asset_link,
            "tags": None,
            "symbol": None,
            "current_bid": current_bid,
            "attributes": {
                "brand": asset_brand
            },
            "currency_code": currency_code,
            "status": status,
            "auction_start": str(offering_start) + " EST",
            "auction_end": str(offering_end) + " EST",
            "base_price": None,
            "bid_increment": None,
            "lot_id": None,
            "lot_name": None,
            "auction_id": None,
            "auction_name": None,
            "auction_type": None,
            "media": [image],
            "custom_data": None,
            "reserve_price": None,
            "winning_bid": None,
            "final_price": None,
            "offering_result": offering_result,
            "bid_count": None,
            "latest_bid": current_bid
        }
        print(json.dumps(asset))

        # start_utc_time = time.strptime(str(offering_start), "%Y-%m-%d %H:%M:%S")
        # offering_start = timegm(start_utc_time)
        # # print("offering_start", offering_start)
        #
        # end_utc_time = time.strptime(str(offering_end), "%Y-%m-%d %H:%M:%S")
        # offering_end = timegm(end_utc_time)


if __name__ == "__main__":
    website_parser()
