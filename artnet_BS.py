import json
from datetime import datetime, timedelta
import requests


def website_parser():
    asset_count = 0
    error_count = 0

    url1 = "https://www.artnet.com/auctions/artworks/load/soonest/?page="
    response = requests.get(url1)
    # print(response)

    try:
        new_response = requests.get(url1)
        print(new_response)
        url1 = "https://www.artnet.com/auctions/artworks/load/soonest/?page="
        page_num = 1
        checker = True
        asset_list = []
        while checker:
            asset_url = url1 + str(page_num)
            print("asset_url", asset_url)
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                'Cookie': 'aoa=837783443313212127.1678431980; incap_ses_706_2666598=drwhKcc6fRpUWh1NHTjMCb75CmQAAAAAN5ePl0xb+UjvkfQBVuW+vA==; visid_incap_2666598=IZHyLnstQF6EN2AxsH6mZ5PPCmQAAAAAQUIPAAAAAAAfqEhghI0UeR6JKfNJqfK2; ASP.NET_SessionId=ggzytmfpq1jzn51gahhxrsrj'
            }
            payload = {}
            response = requests.request("GET", url=asset_url, headers=headers, data=payload)
            print(response.headers['Content-Type'])
            page_num += 1
            if "text/html" in response.headers['Content-Type']:
                print("if")
                checker = False
                print("No data is found ")
            else:
                print("else")
                json_data = json.loads(response.text)
                # print(json_data)
                print("data is present")
                for each_asset in json_data:
                    status, asset = asset_parser(each_asset)
                    asset_list.append(asset)
                    if status == "success":
                        asset_count = asset_count + 1
                    elif status == "error":
                        error_count = error_count + 1
        print("asset_count=", asset_count)
        print("error_count=", error_count)

        print(json.dumps(asset_list))

    except Exception as error:
        print("error in website", error)


def asset_parser(each_asset):
    asset = {}
    try:
        imagelink = []
        # print(each_asset["ImageUrl"])
        asset_image = each_asset["ImageUrl"]
        # print(asset_image)
        imageUrl = {
            "media_type": "image",
            "media_src": asset_image,
            "thumbnail": None,
            "caption": None,
            "is_active": True
        }
        imagelink.append(imageUrl)
        # print(imagelink)

        # print(each_asset['RemainingMiddleText'])

        asset_lastdate = each_asset['Remaining']
        # print(asset_lastdate)
        day = datetime.today()
        # print(day)
        end_auction = day + timedelta(days=each_asset['Remaining']["Days"],
                                      hours=each_asset['Remaining']["Hours"],
                                      minutes=each_asset['Remaining']["Minutes"],
                                      seconds=each_asset['Remaining']["Seconds"])
        print(end_auction)

        # print(each_asset["Title"])
        asset_title = each_asset["Title"]

        # print(each_asset["CurrentBid"])
        asset_currentbid = each_asset["CurrentBid"]

        # print(each_asset["PurchasePrice"])
        asset_purchaseprice = each_asset["PurchasePrice"]

        # print(each_asset["LotId"])
        asset_Id = each_asset["LotId"]

        asset_url = "https://www.artnet.com" + each_asset["DetailsUrl"]
        # print(asset_url)

        asset_bidcount = each_asset["BidsCount"]
        # print(asset_bidcount)

        # print(each_asset["Artist"])
        asset_artist = each_asset["Artist"]

        # print(each_asset["Year"])
        asset_year = each_asset["Year"]

        # print(each_asset["Specialist"])
        asset_specialist = each_asset["Specialist"]

        # print(each_asset["NoFractionCurrentBid"])
        asset_finalprice = each_asset["NoFractionCurrentBid"]

        # print(each_asset["IsSold"])
        asset_status = each_asset["IsSold"]
        if asset_status == False:
            status = "Unsold"
            offering_result = "Available"
        else:
            status = "sold"
            offering_result = "Unavailable"

        if not each_asset["IsSold"]:
            asset = {
                "platform_asset_id": asset_Id,
                "asset_type": "COLLECTIBLE",
                "pricing_type": "auction",
                "name": asset_title,
                "description": None,
                "url": asset_url,
                "tags": None,
                "symbol": None,
                "current_bid": asset_currentbid,
                "attributes": {"asset_year": asset_year,
                               "asset_specialist": asset_specialist,
                               "asset_artist": asset_artist},
                "currency_code": "USD",
                "status": status,
                "auction_start": str(asset_year) + " EST",
                "auction_end": str(end_auction) + " EST",
                "base_price": None,
                "bid_increment": None,
                "lot_id": asset_Id,
                "lot_name": None,
                "auction_id": None,
                "auction_name": None,
                "auction_type": None,
                "media": imagelink,
                "custom_data": {"brand_name": None},
                "reserve_price": None,
                "winning_bid": None,
                "final_price": asset_finalprice,
                "offering_result": offering_result,
                "latest_bid": asset_bidcount,
                "bid_count": asset_currentbid
            }
            # print(asset)

        return "success", asset

    except Exception as error:
        print("try failed ", error)
        return "error", asset


if __name__ == '__main__':
    website_parser()
