import time
from pprint import pprint
from datetime import datetime

import schedule
from ebaysdk.trading import Connection

from ygolegacy.data.cards import Card
from ygolegacy.data.db_session import DbSession
from ygolegacy.data.ebay_listing import EbayPost
from ygolegacy.db_config import EBAY_API_CONFIG


def get_item(item_id, qty):
    api = Connection(config_file=EBAY_API_CONFIG, domain="api.ebay.com", debug=False)
    myitem = {
        'ItemID': item_id
    }
    response = api.execute("GetItem", myitem)
    data = response.dict()
    if data['Ack'] == 'Success':
        item = data['Item']
        pprint(item)
        qty_ebay = item['Quantity']
        sold = item['SellingStatus']['QuantitySold']
        print(qty, qty_ebay, sold)

        if qty != (int(qty_ebay) - int(sold)):
            return True

        #end_date = item['ListingDetails']['EndTime'].split('.')[0]
        #end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
        #return end_date < datetime.now()
        return False
    return False
    # pprint(data, indent=4)


def check_for_updates():
    print('Checking...')
    DbSession.global_init()
    session = DbSession.factory()
    posted_cards = session.query(EbayPost).filter(EbayPost.posted).all()
    print(len(posted_cards), 'cards currently posted...')
    for card in posted_cards:
        main_card = session.query(Card).filter(Card.id == card.id).one()
        check_result = get_item(card.ebay_id, main_card.YGOLEGACY_INVENTORY)
        if not check_result:
            print('not updating yet', card.id)
        if check_result:
            # update listing
            print('updating', card.id, main_card.YGOLEGACY_INVENTORY)
            #print(main_card.YGOLEGACY_INVENTORY)
            if main_card.YGOLEGACY_INVENTORY >= 2:
                main_card.YGOLEGACY_INVENTORY = main_card.YGOLEGACY_INVENTORY - 1
            elif main_card.YGOLEGACY_INVENTORY == 1:
                main_card.YGOLEGACY_INVENTORY = 0
                card.posted = 0
                card.ebay_id = None
                card.price = None
                card.price_value = None
                card.price_type = None
            else:
                card.posted = 0
                card.ebay_id = None
                card.price = None
                card.price_value = None
                card.price_type = None
            print('updated')
            # try:
            #     main_card.YGOLEGACY_INVENTORY = main_card.YGOLEGACY_INVENTORY - 1
            # except Exception as e:
            #     print("EXCEPTION", e)

            session.commit()
    session.close()


if __name__ == '__main__':

    #
    # api = Connection(config_file=EBAY_API_CONFIG, domain="api.ebay.com", debug=False)
    # myitem = {
    #     'ItemID': 164087031838
    # }
    # response = api.execute("GetItem", myitem)
    # pprint(response.dict())
    # exit()

    check_for_updates()
    schedule.every(5).minutes.do(check_for_updates)
    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)
