import time
from pprint import pprint
from typing import Optional, List, Tuple

import requests
import clicksend_client
from clicksend_client import SmsMessage
from clicksend_client.rest import ApiException
from sqlalchemy import or_

from data.cards import Card
from data.db_session import DbSession
from data.notifications import Notification

MANY_CHAT_API = '1285164488326864:8be9c956624030e8dffb1e341b1310c1'

phil_id = 2568111479877941
my_id = 2806140269437674


def get_many_chat_user(subscriber_id: int) -> Optional[Tuple]:
    headers = {
        'Authorization': f"Bearer {MANY_CHAT_API}"
    }
    url = f'https://api.manychat.com/fb/subscriber/getInfo?subscriber_id={subscriber_id}'
    r = requests.get(url, headers=headers)
    data = r.json()['data']
    # Check if user allows for sms notification
    tags = data['tags']
    if not any("AuthNotifSMS" in x['name'] for x in tags):
        print('User has not given authorization for SMS notification.')
        return None, None

    return data.get('phone'), data.get('first_name')


def send_notification(phone: str, body: str):
    if not phone:
        return
    # Configure HTTP basic authorization: BasicAuth
    configuration = clicksend_client.Configuration()
    configuration.username = 'store@ygolegacy.com'
    configuration.password = 'Tomates2019$'

    # create an instance of the API class
    api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
    sms_message = SmsMessage(source="python",
                             body=body,
                             to=phone)
    sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])

    try:
        # Send sms message(s)
        api_response = api_instance.sms_send_post(sms_messages)
        print(api_response)
    except ApiException as e:
        print("Exception when calling SMSApi->sms_send_post: %s\n" % e)



def get_current_notifications() -> List[dict]:
    session = DbSession.factory()
    data = [x.to_dict() for x in session.query(Notification).all()]
    session.close()
    return data


def get_cards_info(ids) -> dict:
    ids = list(set(ids))
    filters = [Card.id == x for x in ids]
    session = DbSession.factory()
    results = session.query(Card).filter(or_(*filters)).all()
    session.close()
    data = {}
    for result in results:
        result: Card
        data[result.id] = result
    return data


def get_current_state() -> dict:
    notifications = get_current_notifications()
    ids = [x['card_id'] for x in notifications]
    prices_and_inventory = get_cards_info(ids)
    return prices_and_inventory


def compare_states(old_state: dict, new_state: dict):
    notifications_dict = {}
    for notif in get_current_notifications():
        if notif['card_id'] in notifications_dict.keys():
            notifications_dict[notif['card_id']].append(notif)
        else:
            notifications_dict[notif['card_id']] = [notif]
    pprint(notifications_dict, indent=4)

    # find newly added
    for key in new_state.keys():
        if key not in old_state.keys():
            old_state[key] = new_state[key]

    # compare values
    for key, value in new_state.items():
        value: Card
        # check if price changed
        if round_price(value.TCGPLAYER_CAD_PRICE) != round_price(old_state[key].TCGPLAYER_CAD_PRICE):
            difference = round_price(value.TCGPLAYER_CAD_PRICE) - round_price(old_state[key].TCGPLAYER_CAD_PRICE)
            diff_str = "Increase" if difference > 0 else "Decrease"
            print('price changed by:', difference)

            for user in notifications_dict[key]:
                phone, name = get_many_chat_user(user['user_id'])
                body = f"""Hi {name}, YGOLEGACY Here!

({value.name}) - ({value.set_code}) - ({value.set_rarity}) - ({value.edition}) - ({value.condition})

Has {diff_str} price from ({round_price(old_state[key].TCGPLAYER_CAD_PRICE)} $CAD) to ({round_price(value.TCGPLAYER_CAD_PRICE)} $CAD).

Here is a direct link to the card: www.ygolegacy.com/{value.set_code.lower()}"""
                send_notification(phone, body)


        else:
            print('no price change')

        # check if inventory changed
        if value.YGOLEGACY_INVENTORY != old_state[key].YGOLEGACY_INVENTORY:
            difference = value.YGOLEGACY_INVENTORY - old_state[key].YGOLEGACY_INVENTORY
            #diff_str = "Increase" if difference > 0 else "Decrease"
            print('inventory changed by:', difference)

            for user in notifications_dict[key]:
                phone, name = get_many_chat_user(user['user_id'])
                body = f"""Hi {name}, YGOLEGACY Here!

({value.name}) - ({value.set_code}) - ({value.set_rarity}) - ({value.edition}) - ({value.condition})

Inventory has change from ({old_state[key].YGOLEGACY_INVENTORY}) to ({value.YGOLEGACY_INVENTORY}).

Here is a direct link to the card: www.ygolegacy.com/{value.set_code.lower()}"""
                send_notification(phone, body)

        else:
            print('no inventory change')


def round_price(price):
    if .01 <= price <= .50:
        price = .25
    elif .51 <= price <= .99:
        price = .95
    else:
        price = float(int(price)) + .95
    return price


def main():
    DbSession.global_init()
    start_state = get_current_state()
    while True:
        new_state = get_current_state()
        compare_states(start_state, new_state)
        start_state = new_state
        time.sleep(10)


if __name__ == '__main__':
    main()
