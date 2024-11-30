from pprint import pprint

from ebaysdk.trading import Connection

from ygolegacy import DbSession
from ygolegacy.data.ebay_listing import EbayPost
from ygolegacy.db_config import EBAY_API_CONFIG


def select_shipping(price: float):
    return [
            {'ExpeditedService': 'false',
             'ShippingService': 'CA_PostLettermail',
             'ShippingServiceCost': '0.95',
             'ShippingServicePriority': '1',
             'ShippingTimeMax': '6',
             'ShippingTimeMin': '2'},
            {'ExpeditedService': 'false',
             'ShippingService': 'CA_PostXpresspost',
             'ShippingServiceCost': '9.95',
             'ShippingServicePriority': '2',
             'ShippingTimeMax': '3',
             'ShippingTimeMin': '1'},
            {'ExpeditedService': 'false',
             'ShippingService': 'CA_Pickup',
             'ShippingServiceCost': '0.0',
             'ShippingServicePriority': '3'}
        ]

def select_shipping_int(price: float):
    if price < 20:
        int_shipping = {
            'ShipToLocation': 'US',
            'ShippingService': 'CA_PostUSALetterPost',
            'ShippingServiceCost': 1.55,
            'ShippingServicePriority': '1',
            'ShippingTimeMax': '10',
            'ShippingTimeMin': '5'
        }
    else:
        int_shipping = {
            'ShipToLocation': 'US',
            'ExpeditedService': 'false',
            'ShippingService': 'CA_PostTrackedPacketsUSA',
            'ShippingServiceCost': '15.95',
            'ShippingServicePriority': '1',
            'ShippingTimeMax': '8',
            'ShippingTimeMin': '3'
        }

    return int_shipping

def create_listing_html(title, img_url):
    html = f"""{title}
"""

    return html


def delete_ebay_posting_in_db(_id):
    session = DbSession.factory()
    card = session.query(EbayPost).filter(EbayPost.ebay_id == _id).first()
    if card:
        card.posted = 0
        card.ebay_id = None
        card.price_value = None
        card.price = None
        card.price_type = None
        card.image = None
        session.commit()
    session.close()
    return card


def delete_item(item_id):
    api = Connection(config_file=EBAY_API_CONFIG, domain="api.ebay.com", debug=False)
    myitem = {
        'ItemID': item_id,
        'EndingReason': 'Incorrect'
    }
    response = api.execute("EndItem", myitem)
    data = response.dict()
    if data['Ack'] == "Success":
        print('deleted ok..')
        delete_ebay_posting_in_db(item_id)
        return True
    return False
    # pprint(data, indent=4)


def add_item(title: str, price: float, img_url: str, qty: str, condition: int = "3000"):
    api = Connection(config_file=EBAY_API_CONFIG, domain="api.ebay.com", debug=False)
    # response = api.execute('GetItem', {'ItemID': 123919789305})
    # title = response.dict()
    # pprint(title['Item'], indent=4)
    # exit()
    myitem = {
        "Item": {
            "Title": title,
            "Description": "<![CDATA[{}]]>".format(create_listing_html(title, img_url)),
            "PrimaryCategory": {"CategoryID": "31395"},
            'StartPrice': price,
            "CategoryMappingAllowed": "true",
            "Country": "CA",
            "Location": "CA",
            "ConditionID": condition,
            "Currency": "CAD",
            "DispatchTimeMax": "3",
            "ListingDuration": "GTC",
            "PaymentMethods": "PayPal",
            "PayPalEmailAddress": "sales@ygolegacy.com",
            "PictureDetails": {"PictureURL": img_url},
            'PostalCode': 'J7X 1A2',
            "Quantity": qty,
            'ShippingDetails': {
                "InternationalShippingServiceOption": select_shipping_int(price),
                "ShippingServiceOptions": select_shipping(price),
                'ShippingType': 'Flat'
            },
            'ReturnPolicy': {'InternationalReturnsAcceptedOption': 'ReturnsNotAccepted',
                             'ReturnsAccepted': 'Returns Not Accepted',
                             'ReturnsAcceptedOption': 'ReturnsNotAccepted'},
            "Site": "Canada"
        }
    }


    response = api.execute("AddFixedPriceItem", myitem)
    data = response.dict()
    _id = data['ItemID']
    return _id


# 'ShipToLocations': ['CA', 'US'],

def update_item(item_id: int, title: str, price: float, img_url: str, qty: str, condition: int = "3000"):
    api = Connection(config_file=EBAY_API_CONFIG, domain="api.ebay.com", debug=False)
    # response = api.execute('GetItem', {'ItemID': 123919789305})
    # title = response.dict()
    # pprint(title['Item'], indent=4)
    # exit()
    myitem = {
        "Item": {
            'ItemID': item_id,
            "Title": title,
            "Description": "<![CDATA[{}]]>".format(create_listing_html(title, img_url)),
            #"Description": title,
            "PrimaryCategory": {"CategoryID": "31395"},
            'StartPrice': price,
            "CategoryMappingAllowed": "true",
            "Country": "CA",
            "Location": "CA",
            "ConditionID": condition,
            "Currency": "CAD",
            "DispatchTimeMax": "3",
            "ListingDuration": "GTC",
            "PaymentMethods": "PayPal",
            "PayPalEmailAddress": "sales@ygolegacy.com",
            "PictureDetails": {"PictureURL": img_url},
            'PostalCode': 'J7X 1A2',
            "ShippingDetails": {
                "InternationalShippingServiceOption": select_shipping_int(price),
                "ShippingServiceOptions": select_shipping(price),
                'ShippingType': 'Flat'
                # 'InternationalShippingServiceOptions': select_shipping(price)
            },
            "Quantity": qty,
            # 'SellerProfiles': {'SellerPaymentProfile': {'PaymentProfileID': '59810106020',
            #                                             'PaymentProfileName': 'PayPal '
            #                                                                   'sales@ygolegacy.com'},
            #                    'SellerReturnProfile': {'ReturnProfileID': '59810105020',
            #                                            'ReturnProfileName': 'Returns '
            #                                                                 'Not '
            #                                                                 'Accepted'},
            #                    'SellerShippingProfile': {'ShippingProfileID': '144128973020',
            #                                              'ShippingProfileName': 'CANADA '
            #                                                                     '0.95 '
            #                                                                     '/ '
            #                                                                     '9.95'}},
            # 'ShippingPackageDetails': {'ShippingIrregular': 'false',
            #                            'ShippingPackage': 'ParcelOrPaddedEnvelope',
            #                            'WeightMajor': {'_measurementSystem': 'Metric',
            #                                            '_unit': 'kg',
            #                                            'value': '0'},
            #                            'WeightMinor': {'_measurementSystem': 'Metric',
            #                                            '_unit': 'gm',
            #                                            'value': '0'}},
            'ReturnPolicy': {'InternationalReturnsAcceptedOption': 'ReturnsNotAccepted',
                             'ReturnsAccepted': 'Returns Not Accepted',
                             'ReturnsAcceptedOption': 'ReturnsNotAccepted'},
            "Site": "Canada"
        }
    }
    print('myitem ', myitem)
    response = api.execute("ReviseFixedPriceItem", myitem)
    data = response.dict()
    _id = data['ItemID']
    return _id

# import os
# os.environ['HTTPS_PROXY'] = ""
# desc = create_listing_html('Test', 'https://i.ebayimg.com/images/g/a7EAAOSwPn1dRy4D/s-l1600.jpg')
# _id = 123940838583 #add_item('Test', desc, 100, 'https://i.ebayimg.com/images/g/a7EAAOSwPn1dRy4D/s-l1600.jpg')
# item = update_item(_id, 'Test', desc, 190, 'https://i.ebayimg.com/images/g/a7EAAOSwPn1dRy4D/s-l1600.jpg')
# print(item)
