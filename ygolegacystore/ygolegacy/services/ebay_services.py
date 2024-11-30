import os
import shutil
import uuid
from sqlalchemy import and_, or_

from ygolegacy.data.db_session import DbSession

from ygolegacy.data.cards import Card
from ygolegacy.data.ebay_listing import EbayPost
from ygolegacy.db_config import EBAY_IMAGES
from ygolegacy.services import ebay_api_services
from ygolegacy.services.site_service import create_sell_price


def download_image(posted_file):
    try:
        input_file = posted_file.file
    except AttributeError:
        return None
    new_file_name = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(EBAY_IMAGES, new_file_name)
    temp_file_path = file_path + '~'
    input_file.seek(0)
    with open(temp_file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)
    os.rename(temp_file_path, file_path)
    return new_file_name


def match_card(_id):
    session = DbSession.factory()
    card = session.query(Card).filter(Card.id == _id).first()
    session.close()
    return card


def match_ebay_posting(_id):
    session = DbSession.factory()
    card = session.query(EbayPost).filter(EbayPost.id == _id).first()
    if not card:
        card = EbayPost(id=_id, posted=False)
        session.add(card)
        session.commit()
        card = session.query(EbayPost).filter(EbayPost.id == _id).first()
    session.close()
    return card

def make_playset(_id):
    session = DbSession.factory()
    session.query(Card).filter(Card.id == _id).update({Card.card_name: Card.name + ' X3'})
    session.close()

def make_presale(_id):
    session = DbSession.factory()
    session.query(Card).filter(Card.id == _id).update({Card.set_code: Card.set_code + ' Presale'})
    session.close()

def post_ebay_product(item_id, value, value_type, image, url_pre_fix, playset, presale, button, image_url):
    card = match_card(item_id)
    session = DbSession.factory()
    ebay_posting = session.query(EbayPost).filter(EbayPost.id == item_id).first()
    image_path = download_image(image)
    if not image_path:
        img_url = image_url
        # rarity = card.set_rarity.lower().strip().replace(' ', '_')
        # edition = card.edition.lower().strip().replace(' ', '_')
        # img_name = "{}_{}_{}.jpg".format(card.set_code.lower().strip(), rarity, edition)
        # # img_url = request.static_url(
        # #     'ygolegacy:static/image/{}.jpg'.format(card.set_code.upper())) if card.set_code else ''
        # img_url = request.static_url(
        #     'ygolegacy:static/image/{}.jpg'.format(img_name)) if card.set_code else ''
    else:
        img_url = url_pre_fix + "/" + image_path
    img_url = img_url.replace('http://', 'https://')
    if value_type == "$":
        price = value
        price_type = 'Manual'
    else:
        cad_price = create_sell_price(card, 'CAD')
        price = cad_price * (value / 100)
        price_type = 'Auto'

    if button == "price":
        ebay_posting.price = price
        ebay_posting.price_value = price if price_type == "Manual" else value / 100
        ebay_posting.price_type = price_type
        session.commit()
        session.close()
        return

    cond_dict = {
        'Near Mint': 'NM',
        'Moderately Played': "MP",
        'Slightly Played': 'SP',
        'Heavily Played': 'HP'
    }

    card_name = card.name + ' X3' if playset else card.name
    set_code = card.set_code + ' Presale' if presale else card.set_code

    if '1st' in card.edition:
        title = f"{card_name} {set_code} {card.set_rarity} 1st {cond_dict[card.condition]} Yugioh"
    else:
        title = f"{card_name} {set_code} {card.set_rarity} {cond_dict[card.condition]} Yugioh"

    print('title ', title)

    title = title.replace('&', "and")
    title = title[:70]  # Shorten to 70 char title limit

    if not ebay_posting:
        ebay_id = ebay_api_services.add_item(title, price, img_url, str(card.YGOLEGACY_INVENTORY))
        ebay_posting = EbayPost(id=item_id, posted=True, price_value=price if price_type == "Manual" else value/100,
                                image=img_url, ebay_id=ebay_id, price_type=price_type, price=price)
        session.add(ebay_posting)
    elif ebay_posting.posted is False:
        ebay_id = ebay_api_services.add_item(title, price, img_url, str(card.YGOLEGACY_INVENTORY))
        ebay_posting.posted = True
        ebay_posting.price_value = price if price_type == "Manual" else value/100
        ebay_posting.image = img_url
        ebay_posting.ebay_id = ebay_id
        ebay_posting.price_type = price_type
        ebay_posting.price = price
    else:
        ebay_api_services.update_item(ebay_posting.ebay_id, title, price, img_url, str(card.YGOLEGACY_INVENTORY))
        ebay_posting.posted = True
        ebay_posting.price_value = price if price_type == "Manual" else value/100
        ebay_posting.image = img_url
        ebay_posting.price_type = price_type
        ebay_posting.price = price
    session.commit()
    session.close()
    pass


# 1 Group 10$+
# 2 Group 4$+ to 9.99$
# 3 group 0.95$ to 3.99$
# 4 Group 0.00$ to 0.94$

def get_ebay_for_group(group: int):
    session = DbSession.factory()
    if group == 0:
            cards = session.query(Card).filter(
                and_(Card.YGOLEGACY_INVENTORY > 0,
                Card.ebayca_avg_cad_low == 0)
            )
    elif group == 1:
        cards = session.query(Card).filter(
            and_(Card.YGOLEGACY_INVENTORY > 0,
            Card.ebayca_avg_cad_low >= 10)
        )
    elif group in range(2, 4):
        cards = session.query(Card).filter(
            Card.YGOLEGACY_INVENTORY > 0,
            and_(Card.ebayca_avg_cad_low < 10,
                 Card.ebayca_avg_cad_low >= 4)
        )
        limit = int(cards.count()/2)
        cards = cards.limit(limit).offset((group - 2) * limit)
    elif group in range(4, 7):
        cards = session.query(Card).filter(
            Card.YGOLEGACY_INVENTORY > 0,
            and_(Card.ebayca_avg_cad_low < 4,
                 Card.ebayca_avg_cad_low >= 2)
        )
        limit = int(cards.count()/3)
        cards = cards.limit(limit).offset((group - 3) * limit)
    elif group in range(7, 26):
        cards = session.query(Card).filter(
            Card.YGOLEGACY_INVENTORY > 0,
            and_(Card.ebayca_avg_cad_low < 2,
                 Card.ebayca_avg_cad_low > 0)
        )
        limit = int(cards.count()/19)
        cards = cards.limit(limit).offset((group - 6) * limit)
    # elif group == 3:
    #     cards = session.query(Card).filter(
    #         Card.YGOLEGACY_INVENTORY > 0,
    #         and_(Card.TCGPLAYER_CAD_PRICE < 4,
    #              Card.TCGPLAYER_CAD_PRICE >= .95)
    #     )
    # elif group == 4:
    #     cards = session.query(Card).filter(
    #         Card.YGOLEGACY_INVENTORY > 0,
    #         and_(Card.TCGPLAYER_CAD_PRICE < .95,
    #              Card.TCGPLAYER_CAD_PRICE >= 0)
    #     )
    else:
        cards = session.query(Card).filter(
            Card.YGOLEGACY_INVENTORY > 0
        )

    cards = cards.all()
    session.close()
    return cards

def get_above_10_avg(below=False):
    session = DbSession.factory()
    all_above_10 = session.query(Card) \
        .filter(
        and_(
            Card.YGOLEGACY_INVENTORY > 0,
            or_(round_price(Card.EBAYCA_CAD_PRICE) < 10 if below else Card.EBAYCA_CAD_PRICE >= 10,
                Card.AVG_CAD_PRICE is None))).all()
    session.close()

    return all_above_10


def make_html_from_results(result_list, request, ebay_page):
    html_all = ''
    for item in result_list:
        ebay_posting = match_ebay_posting(item.id)
        buy_cad = create_sell_price(item, 'CAD', True)
        buy_usd = create_sell_price(item, 'USD', True)
        avg_cad = "{:.2f}$".format(float(item.AVG_CAD_PRICE)) if item.AVG_CAD_PRICE else "-"
        avg_usd = "{:.2f}$".format(float(item.AVG_CAD_PRICE)) if item.AVG_CAD_PRICE else "-"
        # if item.id == 35:
        #     print("ID", item.YGOLEGACY_INVENTORY)


        set_code = item.set_code
        if set_code:
            rarity = item.set_rarity.lower().strip().replace(' ', '_') if item.set_rarity else None
            edition = item.edition.lower().strip().replace(' ','_')
            img_name = "{}_{}_{}.jpg".format(set_code.lower().strip(), rarity, edition)
            alt_img_name = "{}_{}_{}.jpg".format(set_code.lower().strip(), rarity, 'unlimited' if edition != 'unlimited' else '1st_edition')
            image = request.static_url(
                'ygolegacy:static/img_ygo/{}'.format(img_name))
            alt_image = request.static_url(
                'ygolegacy:static/img_ygo/{}'.format(alt_img_name))
        else:
            image = None
            alt_image = None
        # alt_image = None
        # image = None

        ebay_ca_url = item.ebayca_url
        ebay_com_url = item.ebaycom_url
        tcg_url = item.tcg_url
        tnt_url = item.tnt_url
        ftfg_url = item.ftfg_url
        ebay_ca_results = "<small>({})</small>".format(item.ebayca_results) if item.ebayca_results else ""
        ebay_com_results = "<small>({})</small>".format(item.ebaycom_results) if item.ebaycom_results else ""
        tcg_results = "<small>({})</small>".format(item.tcg_results) if item.tcg_results else ""
        tnt_results = "<small>({})</small>".format(item.tnt_results) if item.tnt_results else ""
        ftfg_results = "<small>({})</small>".format(item.ftfg_results) if item.ftfg_results else ""
        last_updated = f'<li class="edition">{item.last_updated}</li>' if item.last_updated else "no last update"
        html = f"""
                            <section {'style="background-color: green;"' if ebay_posting.posted else ''} class="sec1" id="{item.id}" >
                    
                    <div class="container">
                    <div class="row">
                    <div class="col-sm-3 col-3">
                        <div class="imgg">
                    	
                    		<img src="{image}" onerror="this.onerror=null;this.src='{alt_image}';" class="img-fluid" alt="img1">
                    	</div>
                    </div>
                    <div class="col-sm-6 col-7">
                    <div class="main-middle">
                    <div class="middle_content">
                    <h2>{item.name + " ({}CAD {}USD)".format(buy_cad, buy_usd) if item.name else 'null'}</h2>
                    <ul>
                        <li>{item.set_name if item.set_name else 'None'}</li>
                        <li>{item.set_rarity if item.set_rarity else 'None'}</li>
                        <li class="set_code">{item.set_code if item.set_code else 'None'}</li>
                        <li class="edition">{item.edition if item.edition else 'None'}</li>
                        <li class="edition">{item.condition if item.condition else 'None'}</li>
                        {last_updated}
                    </ul>

                    </div>
            <div class="bottm_content">
            <div class="row">
                <div class="col-sm-4 col-4">
                <h4>EBAY.CA {ebay_ca_results}</h4>
                <p onclick="openInNewTab('{ebay_ca_url}');" style="cursor:pointer;"><strong class="ebayca_cad">{"{:.2f}$<small>CAD</small>".format(item.EBAYCA_CAD_PRICE) if item.EBAYCA_CAD_PRICE else '---'}</strong>
                </p>
                <p>LOW {"{:.2f}$".format(item.ebayca_avg_cad_low) if item.ebayca_avg_cad_low else '-'}</p>
                <p>HIGH {"{:.2f}$".format(item.ebayca_avg_cad_high) if item.ebayca_avg_cad_high else '-'}</p>
                <p onclick="openInNewTab('{ebay_ca_url}');" style="cursor:pointer;">
                    <strong class="ebayca_usd">{"{:.2f}$<small>USD</small>".format(item.EBAYCA_USD_PRICE) if item.EBAYCA_USD_PRICE else '---'}</strong>
                </p>
                <p>LOW {"{:.2f}$".format(item.ebayca_avg_usd_low) if item.ebayca_avg_usd_low else '-'}</p>
                <p>HIGH {"{:.2f}$".format(item.ebayca_avg_usd_high) if item.ebayca_avg_usd_high else '-'}</p>
                </div>  
                <div class="col-sm-4 col-4">
                <h4>EBAY.COM {ebay_com_results}</h4>
                <p onclick="openInNewTab('{ebay_com_url}');" style="cursor:pointer;">   
                    <strong class="ebaycom_cad">{"{:.2f}$<small>CAD</small>".format(item.EBAYCOM_CAD_PRICE) if item.EBAYCOM_CAD_PRICE else '---'}</strong>
                </p>
                <p>LOW {"{:.2f}$".format(item.ebaycom_avg_cad_low) if item.ebaycom_avg_cad_low else '-'}</p>
                <p>HIGH {"{:.2f}$".format(item.ebaycom_avg_cad_high) if item.ebaycom_avg_cad_high else '-'}</p>
                <p onclick="openInNewTab('{ebay_com_url}');" style="cursor:pointer;"><strong class="ebaycom_usd">{"{:.2f}$<small>USD</small>".format(item.EBAYCOM_USD_PRICE) if item.EBAYCOM_USD_PRICE else '---'}</strong>
                <p>LOW {"{:.2f}$".format(item.ebaycom_avg_usd_low) if item.ebaycom_avg_usd_low else '-'}</p>
                <p>HIGH {"{:.2f}$".format(item.ebaycom_avg_usd_high) if item.ebaycom_avg_usd_high else '-'}</p>
                </div>
                <div class="col-sm-4 col-4">
                <h4>TCGPLAYER {tcg_results}</h4>
                <p onclick="openInNewTab('{tcg_url}');" style="cursor:pointer;">
                    <strong class="tcg_cad">{"{:.2f}$<small>CAD</small>".format(item.TCGPLAYER_CAD_PRICE) if item.TCGPLAYER_CAD_PRICE else '---'}</strong>
                </p>
                <p>LOW {"{:.2f}$".format(item.tcg_avg_cad_low) if item.tcg_avg_cad_low else '-'}</p>
                <p>HIGH {"{:.2f}$".format(item.tcg_avg_cad_high) if item.tcg_avg_cad_high else '-'}</p>
                <p onclick="openInNewTab('{tcg_url}');" style="cursor:pointer;">
                    <strong class="tcg_usd">{"{:.2f}$<small>USD</small>".format(item.TCGPLAYER_USD_PRICE) if item.TCGPLAYER_USD_PRICE else '---'}</strong>
                </p>
                <p>LOW {"{:.2f}$".format(item.tcg_avg_usd_low) if item.tcg_avg_usd_low else '-'}</p>
                <p>HIGH {"{:.2f}$".format(item.tcg_avg_usd_high) if item.tcg_avg_usd_high else '-'}</p>
                </div>
            </div>
            
            <div class="row">
                <div class="col-sm-4 col-4">
                <h4>TrollnToad {tnt_results}</h4>
                <p onclick="openInNewTab('{tnt_url}');" style="cursor:pointer;"><strong class="tnt_cad">{"{:.2f}$<small>CAD</small>".format(item.tnt_cad_price) if item.tnt_cad_price else '---'}</strong>
                </p>
                <p>LOW {"{:.2f}$".format(item.tnt_avg_cad_low) if item.tnt_avg_cad_low else '-'}</p>
                <p>HIGH {"{:.2f}$".format(item.tnt_avg_cad_high) if item.tnt_avg_cad_high else '-'}</p>
                <p onclick="openInNewTab('{tnt_url}');" style="cursor:pointer;">
                    <strong class="tnt_usd">{"{:.2f}$<small>USD</small>".format(item.tnt_usd_price) if item.tnt_usd_price else '---'}</strong>
                </p>
                <p>LOW {"{:.2f}$".format(item.tnt_avg_usd_low) if item.tnt_avg_usd_low else '-'}</p>
                <p>HIGH {"{:.2f}$".format(item.tnt_avg_usd_high) if item.tnt_avg_usd_high else '-'}</p>
                </div>  
                <div class="col-sm-4 col-4">
                <h4>FacetoFace {ftfg_results}</h4>
                <p onclick="openInNewTab('{ftfg_url}');" style="cursor:pointer;">   
                    <strong class="ftfg_cad">{"{:.2f}$<small>CAD</small>".format(item.ftfg_cad_price) if item.ftfg_cad_price else '---'}</strong>
                </p>
                <p>LOW {"{:.2f}$".format(item.ftfg_avg_cad_low) if item.ftfg_avg_cad_low else '-'}</p>
                <p>HIGH {"{:.2f}$".format(item.ftfg_avg_cad_high) if item.ftfg_avg_cad_high else '-'}</p>
                <p onclick="openInNewTab('{ftfg_url}');" style="cursor:pointer;"><strong class="ftfg_usd">{"{:.2f}$<small>USD</small>".format(item.ftfg_usd_price) if item.ftfg_usd_price else '---'}</strong>
                <p>LOW {"{:.2f}$".format(item.ftfg_avg_usd_low) if item.ftfg_avg_usd_low else '-'}</p>
                <p>HIGH {"{:.2f}$".format(item.ftfg_avg_usd_high) if item.ftfg_avg_usd_high else '-'}</p>
                </div>
                
                <div class="col-sm-4 col-4">
                <h4>Sell Price</h4>
                <p >   
                    <strong class="ftfg_cad">{"{:.2f}$<small>CAD</small>".format(create_sell_price(item, 'CAD')) if item.ebayca_avg_cad_low else '---'}</strong>
                </p>
               
                <p><strong class="ftfg_usd">{"{:.2f}$<small>USD</small>".format(create_sell_price(item, 'USD')) if item.ebayca_avg_usd_low else '---'}</strong>
                </div>
            	</div>
            </div>
						</div>
						</div>
						<div class="col-sm-3 col-2">
							<div class="rght_bx">
								<form action="/live/postEbay" enctype="multipart/form-data">
									<input type="hidden" name="item_id" value="{item.id}">
									<input type="hidden" name="image_url" value="{image}">
									<div>
										<fieldset id="group" style="color: white;">
											<input type="radio" value="$" name="valueType" checked> $
											<input type="radio" value="%" name="valueType"> %
										</fieldset>
										<div>
												SELL
											<input type="text" {'value="${:.2f}"'.format(ebay_posting.price) if ebay_posting.price else 'placeholder="value"'} name="value">
											<input style="color: white;" type="file" value="" name="image">
										</div>
										<input type="hidden" name="ebay_page" value="{ebay_page}">
										<button type="submit" item-id="{item.id}" name="update_btn" value="ebay">Sell on eBay</button>
										<button type="submit" item-id="{item.id}" name="update_btn" value="price">Save Price</button>
										<button type="submit" item-id="{item.id}" name="update_btn" value="delete" {'disabled'if  not ebay_posting.posted else ''}>Delete Listing</button>
										<input type="checkbox" id="playset" name="playset" /><label for="playset" style="color: white;">Playset</label>
										<input type="checkbox" id="presale" name="presale" /><label for="presale" style="color: white;">Presale</label>
										<input type="hidden" name="ebay_id" value="{ebay_posting.ebay_id}">
										<p style="color: white;">{"Posted for $" + '{:.2f} {}'.format(ebay_posting.price, "("+str(int(ebay_posting.price_value*100))+"%)" if ebay_posting.price_type == 'Auto' else '') if ebay_posting.posted else 'Not posted'}</p>
										<p style="color: white;">{"Inventory: " + str(item.YGOLEGACY_INVENTORY) if item.YGOLEGACY_INVENTORY else "0"}</p>
								</form>
						</div>
						</div>
						</div>
						</div>
						</section>
                            """
        html_all += html
    return html_all




def round_price(price):
    if .01 <= price <= .50:
        price = .25
    elif .51 <= price <= .99:
        price = .95
    else:
        price = float(int(price)) + .95
    return price



def find_card_by_id(card_id):
    session = DbSession.factory()
    return session.query(Card).filter(Card.id == card_id).first()