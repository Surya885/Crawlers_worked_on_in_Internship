import json
from asyncio.log import logger
from datetime import datetime
import lxml
import requests
from bs4 import BeautifulSoup

def website_parser():
    asset_list = []

    url= "https://api.netcapital.com/v2/offerings?limit=12&orderby=trending&page="

    page_num = 1
    checker = True
    while checker:
        asset_url = url + str(page_num)
        print("asset_url", asset_url)
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
        payload = {}
        response = requests.request("GET",url=asset_url,headers=headers,data=payload)
        page_num += 1
        if len(json.loads(response.text))==0:
            checker = False
            print("No data is found ")
        else:
            print("else")
            # print(response.text)
            json_data =json.loads(response.text)
            # print(json_data)
            for each_data in json_data:
                asset = parser(each_data)
                asset_list.append(asset)
    print(json.dumps(asset_list))

def parser(each_data):

    try:
        image_list = []
        asset_valuation = None
        asset_video_url = None
        asset_offering_price = None
        asset_total_price = None
        asset_deadline = None
        asset_off_pdf = None


        # print(each_data["code"])
        data_url = "https://netcapital.com/companies/" + each_data["code"]
        print(data_url)
        offering_price_per_share = each_data["pricePerUnit"]
        # print("offering_price_per_share",offering_price_per_share)
        asset_start_date = each_data["startDate"]
        date_string = asset_start_date
        date_time = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        asset_start_date = date_time.strftime("%Y-%m-%d %H:%M:%S %Z")
        # print("asset_start_date",asset_start_date)
        asset_end_date = each_data["endDate"]
        date_string = asset_end_date
        date_time = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        asset_end_date = date_time.strftime("%Y-%m-%d %H:%M:%S %Z")
        # print("asset_end_date", asset_end_date)
        asset_allocated_quantity = each_data["allocatedQuantity"]
        # print("asset_allocated_quantity", asset_allocated_quantity)
        asset_offer_Status = each_data["offerStatus"]
        # print("asset_offer_Status" , asset_offer_Status)
        asset_id = each_data["entityKey"]
        # print("asset_id", asset_id)


        response = requests.get(data_url)
        # print(response.text)
        soup = BeautifulSoup(response.content,"lxml")
        # print(soup.prettify())

        if soup.find("div", class_="hero-flex-container") is not None:
            asset_deadline = soup.find("div", class_="hero-flex-container")\
                .find("div", class_="intro__sidebar stats") \
                .find("div", class_="time-remaining stats__item")\
                .find("div", class_="stats__wrapper")\
                .find("div",class_="stats__value stats__value--accent").text
            # print(asset_deadline)

            asset_valuation = soup.find("div", class_="hero-flex-container")\
                .find("div", class_="intro__sidebar stats") \
                .find("div", class_="valuation stats__item")\
                .find("div", class_="stats__value").text
            asset_valuation  = "".join(asset_valuation).replace("$","")
            # print(asset_valuation)

            asset_offering_price = soup.find("div", class_="hero-flex-container")\
                .find("div", class_="intro__sidebar stats") \
                .find("div", class_="share-price stats__item")\
                .find("div", class_="stats__value").text
            asset_offering_price = "".join(asset_offering_price).replace("$","")
            # print(asset_offering_price)

            asset_total_price = soup.find("div", class_="hero-flex-container")\
                .find("div", class_="intro__sidebar stats") \
                .find("div", class_="funding-progress stats__item")\
                .find("div", class_="stats__value").text
            asset_total_price = "".join(asset_total_price).replace("$","")
            # print(asset_total_price)

            asset_image = soup.find_all("img", class_="section-figure__img")
            # print(asset_image)

            for i in asset_image:
                # print(i["src"])
                image_list = []
                asset_media_url = "https:" + i["src"]
                # print(asset_media_url)
                thumbnail = {
                    "media_type": "image",
                    "media_src": asset_media_url,
                    "thumbnail": None,
                    "caption": None,
                    "is_active": True
                }
                image_list.append(thumbnail)
                # print(image_list)

            asset_video_url = soup.find("div", class_="intro__hero-content")\
                .find("div", class_="intro-video") \
                .find("img", class_="intro-video__img")["src"]
            asset_video_url = "https:" + asset_video_url
            # print(asset_video_url)

            asset_latest_offering_statement = soup.find(id="overview") \
                .find("div", class_="company-sections tabs").find("div", class_="tab").find("section",class_="section filings") \
                .find("div", class_="section__content").find("a", class_="file track-download")["href"]
            asset_off_pdf = "https:" + asset_latest_offering_statement
            # print(asset_off_pdf)

        elif soup.find(id="overview") is not None:
            asset_deadline = soup.find(id="overview")\
                 .find("div", class_="hero")\
                .find("div", class_="container")\
                .find("div",class_="wrap")\
                .find("div",class_="sidebar") \
                .find("li", class_="time-remaining")\
                .find("div", class_="title").text
            # print(asset_deadline)

            asset_valuation = soup.find(id="overview")\
                .find("div", class_="hero")\
                .find("div", class_="container")\
                .find("div",class_="wrap")\
                .find("div", class_="sidebar") \
                .find("li", class_="valuation")\
                .find("div", class_="value").text
            asset_valuation = "".join(asset_valuation).replace("$", "")
            # print(asset_valuation)

            asset_offering_price = soup.find(id="overview")\
                .find("div", class_="hero")\
                .find("div", class_="container")\
                .find("div",class_="wrap")\
                .find("div", class_="sidebar") \
                .find("li", class_="share-price")\
                .find("div", class_="value").text
            asset_offering_price = "".join(asset_offering_price).replace("$","")
            # print(asset_offering_price)

            asset_total_price = soup.find(id="overview")\
                .find("div", class_="hero")\
                .find("div", class_="container") \
                .find("div", class_="wrap") \
                .find("div", class_="sidebar") \
                .find("li", class_="funding-progress")\
                .find("div", class_="value")\
                .find("span",class_="amount-raised").text
            asset_total_price = "".join(asset_total_price).replace("$", "")
            # print(asset_total_price)

            asset_image = soup.find_all("img", class_="lazyload")
            # print(asset_image)

            for i in asset_image:
                # print(i["data-src"])
                image_list = []
                asset_media_url = "https:" + i["data-src"]
                # print(asset_media_url)
                thumbnail = {
                    "media_type": "image",
                    "media_src": asset_media_url,
                    "thumbnail": None,
                    "caption": None,
                    "is_active": True
                }
                image_list.append(thumbnail)
            # print(image_list)

            asset_video_url =soup.find(id="overview")\
                .find("div", class_="hero")\
                .find("div", class_="container")\
                .find("div",class_="hero-content") \
                .find("div", class_="equal-height")\
                .find("a")["href"]
            # print(asset_video_url)

            asset_latest_offering_statement = soup.find(id="overview") \
                .find("div", class_="company-sections tabs")\
                .find("div", class_="tab").find("section",class_="section filings") \
                .find("div", class_="section__content")\
                .find("a", class_="file track-download")["href"]
            asset_off_pdf = "https:" + asset_latest_offering_statement
            # print(asset_off_pdf)

        net_url = "https://api.netcapital.com/listings/"+ str(asset_id) +"?req=i3x8b&query=%7B%22expansions%22%3A%5B%7B%22relationName%22%3A%22images%22%7D%5D%2C%22views%22%3A%5B%5D%7D"
        response = requests.get(net_url)
        # print(response.text)
        my_json_data = json.loads(response.text)
        # print(my_json_data)
        cik = my_json_data["cik"]
        description = my_json_data["businessSummary"]
        date_of_formation = my_json_data["dateOfFormation"]
        company_legal_name = my_json_data["legalName"]
        company_Formation_Type = my_json_data["companyFormation"]
        asset_security_type = my_json_data["equitySecurities"]
        # print(asset_security_type)


        business_details, regulatory_obj, offering_obj, sec_request_url, regulation_type = cik_parser(cik,asset_id )
    
        asset={
                "asset_url":data_url,
               "offering_price_per_share":offering_price_per_share,
               "asset_start_date":asset_start_date,
               "asset_end_date":asset_end_date,
               "allocate_quantity":asset_allocated_quantity,
               "offer_status":asset_offer_Status,
                "asset_key":asset_id,
                "asset_deadline":asset_deadline,
                "asset_valuation":asset_valuation,
                "asset_offering_price":asset_offering_price,
                "asset_total_amount_raised":asset_total_price,
                "asset_images":image_list,
                "asset_video_url":asset_video_url,
                "cik":cik,
                "description":description,
                "date_of_formation":date_of_formation,
                "company_legal_name":company_legal_name,
                "asset_off_pdf":asset_off_pdf,
                "regulation_type":regulation_type,
                "sec_request_url":sec_request_url,
                "offering_obj":offering_obj,
                "regulatory_obj":regulatory_obj,
                "business_details":business_details,
                "company_Formation_Type":company_Formation_Type,
                "Security_Subtype":asset_security_type
             }

        # print(asset)
        # print(json.dumps(asset))
        return asset

    except Exception as Error:
        print("this asset has error",Error)

if __name__ == '__main__':
    # print("yes")
    website_parser()
    data_url ="https://netcapital.com/companies/hiveskill"