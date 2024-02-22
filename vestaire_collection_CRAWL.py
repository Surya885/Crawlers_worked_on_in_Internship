from bs4 import BeautifulSoup
import requests
import lxml
import datetime, time
import json
from calendar import timegm


def website_parser():

    loop_checker = True
    offset = 0
    try:
        filter_list = [
            {
                "catalogLinksWithoutLanguage": ["/women-bags/"], "universe.id": ["1"],
                "price": {">=": 1000000}
            },
            {
                "catalogLinksWithoutLanguage": ["/men-accessories/watches/"], "universe.id": ["2"],
                "price": {">=": 1000000}
            },
            {
                "catalogLinksWithoutLanguage": ["/women-accessories/watches/"], "universe.id": ["1"],
                "price": {">=": 1000000}
            }
        ]
        for each_filter in filter_list:
            while loop_checker:
                url = "https://search.vestiairecollective.com/v1/product/search"

                payload = json.dumps({
                    "pagination": {
                        "offset": offset,
                        "limit": 200
                    },
                    "fields": [
                        "name",
                        "description",
                        "brand",
                        "model",
                        "country",
                        "price",
                        "discount",
                        "link",
                        "sold",
                        "likes",
                        "editorPicks",
                        "shouldBeGone",
                        "seller",
                        "directShipping",
                        "local",
                        "pictures",
                        "colors",
                        "size",
                        "stock",
                        "universeId"
                    ],
                    "facets": {
                        "fields": [
                            "brand",
                            "universe",
                            "country",
                            "stock",
                            "color",
                            "categoryLvl0",
                            "priceRange",
                            "price",
                            "condition",
                            "region",
                            "editorPicks",
                            "watchMechanism",
                            "discount",
                            "sold",
                            "directShippingEligible",
                            "directShippingCountries",
                            "localCountries",
                            "sellerBadge",
                            "isOfficialStore",
                            "materialLvl0",
                            "size0",
                            "size1",
                            "size2",
                            "size3",
                            "size4",
                            "size5",
                            "size6",
                            "size7",
                            "size8",
                            "size9",
                            "size10",
                            "size11",
                            "size12",
                            "size13",
                            "size14",
                            "size15",
                            "size16",
                            "size17",
                            "size18",
                            "size19",
                            "size20",
                            "size21",
                            "size22",
                            "size23",
                            "dealEligible"
                        ],
                        "stats": [
                            "price"
                        ]
                    },
                    "q": None,
                    "sortBy": "relevance",
                    "filters": each_filter,

                    "locale": {
                        "country": "US",
                        "currency": "USD",
                        "language": "us",
                        "sizeType": "US"
                    },
                    "mySizes": None
                })
                headers = {
                    'Content-Type': 'application/json',
                    'Cookie': '__cf_bm=pBRAfy.tLtqYMC3vOTmjxfqMkx3NxanNsbowY1d1A8g-1676884289-0-ATxJtbCTKWxmrRafMmhXnSt1/CHB8gEGU7qa2nOl358zTXZNq+0rCV7Mhk18sgra1STB7Z1J+WoJC8ldkho/gd4=; __cflb=0H28v5tgc1KNbuX24caCBoFTnHS8EwhpJ3baQ1ADHB5'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                print(response)

                json_data = json.loads(response.content)

                if "paginationStats" not in json_data:
                    loop_checker = False
                else:
                    for each_item in json_data["items"]:
                        asset_link = "https://us.vestiairecollective.com/" + each_item["link"]
                        asset_id = each_item["id"]
                        if each_item["sold"]:
                            status = "OFFERING_CLOSED"
                        else:
                            status = "OFFERING_OPEN"


    except Exception as e:
        print("error in auction parser :", e)


def asset_parser(asset_link, asset_id, status):
    global prod_resp, resp
    asset_name = None
    pc_id = None
    offering_end_date = None
    asset_description = ""
    environment = ["dev", "prod"]
    offering_result = "UNSOLD"
    image_list = []

    try:
        print(asset_link, asset_id, status)
        asset_id = str(asset_id)
        response = requests.get(asset_link)
        # print(response)

        listing_details = BeautifulSoup(response.text, 'lxml')

        listing_title = listing_details.find("main", class_="p_productPage__0n7Zp").find("div",class_="p_productPage__top__WvHGB innerContainer")\
        .find("div",class_="p_productPage__top__title__aojOc").find("h1",class_="product-main-heading_productTitle__mwnbv")\
        .find("div",class_="vc-title-l product-main-heading_productTitle__brand___s2rF").text
        # print(listing_title)

        image_details = listing_details.find(class_="p_productPage__0n7Zp").find(
            class_="p_productPage__top__WvHGB innerContainer") \
            .find(class_="p_productPage__top__image__kNYZ4")
        # print(image_details)
        if image_details.find(class_="product-gallery_pdtImg__pXmPX") is not None:
            for each_image in image_details.find(class_="product-gallery_pdtImg__main__O9Z7F"):
                # print(each_image)
                # print(each_image.img["src"])
                imageUrl = {
                    "media_type": "image",
                    "media_src": each_image.img["src"],
                    "thumbnail": None,
                    "caption": None,
                    "is_active": True
                }
                image_list.append(imageUrl)

            # print(image_list)

        new_image = listing_details.find("div", id="__next").find("div", class_="en-US hasAccessibilityLink").find("main", class_="p_productPage__0n7Zp") \
            .find("div", class_="p_productPage__top__WvHGB innerContainer").find("div", class_="p_productPage__top__image__kNYZ4") \
            .find("div", class_="product-gallery_pdtImg__pXmPX").find("div",class_="product-gallery_pdtImg__main__O9Z7F") \
            .find("div", class_="product-gallery_slide___c4ua product-gallery_custom__H85rn").find("div",class_="vc-images_imageContainer__D7OIG")
        new_image = new_image.img["src"]
        thumbnail = {
            "media_type": "image",
            "media_src": new_image,
            "thumbnail": None,
            "caption": None,
            "is_active": True
        }
        image_list.append(thumbnail)
        # print(image_list)

        price_detail = listing_details.find("div", {"id": "__next"}).find(class_="p_productPage__0n7Zp").find(class_="p_productPage__top__infos__lgDxJ")\
            .find(class_="product-details_productDetails__qxKw8").find( class_="product-details_productDetails__top__7zBXS")\
            .find(class_="product-details_productDetails__resume__j0l_A").find("div",class_="product-details_productDetails__resume__productPrice__ycNwl")
        # print("price_detail",price_detail)
        current_price = price_detail.find("span").text
        # print(current_price)
        if "Sold at" in current_price:
            asset_price = str(current_price).split("on")[0].replace("Sold at ", "").replace("$", "").replace(",","").replace(" ", "")
            print("asset_price", asset_price)
            status = "OFFERING_CLOSED"
            offering_result = "SOLD"
        else:
            asset_price = str(current_price).replace("$", "").replace(",", "")
        # print("asset_price", asset_price)

        asset_description_details = listing_details.find(class_="p_productPage__0n7Zp").find(
            class_="p_productPage__top__infos__lgDxJ") \
            .find(class_="product-details_productDetails__qxKw8").find(
            class_="product-details_productDetails__top__7zBXS") \
            .find(class_="product-details_productDetails__resume__j0l_A").find(class_="product-details_productDetails__resume__characteristics__AkhuD")
        # print(asset_description_details)

        for each_p_tag in asset_description_details.findAll("p"):
            # print(each_p_tag)
            asset_description = asset_description + "\n" + each_p_tag.text
        # print(asset_description)

        general_description_details = listing_details.find("div", {"id": "__next"}).find(class_="p_productPage__0n7Zp") \
            .find("section", class_="p_productPage__moreDetails__xiZa4").find(class_="innerContainer") \
            .find(class_="product-description_description__container__YJ_DM") \
            .find(class_="product-description_description__container__core__77D0I")
        # print(general_description_details)

        genral_info = {}

        more_details = general_description_details.find("div",class_="product-description-list_descriptionList__GEIG9 d-md-flex d-none") \
            .find(class_="product-description-list_descriptionList__column__ndidZ product-description-list_descriptionList__column--left__D8e9D") \
            .find(class_="product-description-list_descriptionList__block__DKb4B")
        # print("more_details", more_details)
        ul_tag_info = more_details.find("ul", class_="product-description-list_descriptionList__list__FJb05")
        # print(ul_tag_info)
        all_li_tags = ul_tag_info.findAll("li", class_="product-description-list_descriptionList__listItem__Dw4lT")
        for each_li in all_li_tags:
            dict_key = each_li.find("span", class_="product-description-list_descriptionList__property__MPK2a").text
            dict_key = dict_key.replace(":", "")
            dict_value = each_li.find("span", class_="product-description-list_descriptionList__value__lJeA_").text
            # print(dict_key+"  "+dict_value)
            genral_info[dict_key] = dict_value

        # print(genral_info)


        brand_name = genral_info["Designer"]
        # if status == "OFFERING_CLOSED":
        #     offering_end_date = str(datetime.datetime.now())
        # print("today ",datetime.datetime.now())

        asset = {
            "platform_asset_id": asset_id,
            "name": asset_name,
            "description": asset_description,
            "url": asset_link,
            "tags": [],
            "symbol": None,
            "offering_start": None,
            "offering_end": None,
            "attributes": {
                "brand_name": brand_name,
                "specifications": genral_info
            },
            "currency_code": "USD",
            "status": status,
            "media": image_list,
            "custom_data": None,
            "sale_price": asset_price,
            "offering_result": offering_result
        }

        print(json.dumps(asset))

if __name__ == '__main__':
    website_parser()
    asset_parser("https://us.vestiairecollective.com//women-bags/handbags/hermes/yellow-alligator-kelly-25-hermes-handbag-31868869.shtml", "31868869", "OFFERING_OPEN")
