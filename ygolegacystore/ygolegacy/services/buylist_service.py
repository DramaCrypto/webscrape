from operator import and_, or_

from ygolegacy.data.cards import Card
from ygolegacy.data.db_session import DbSession
from ygolegacy.services.site_service import create_sell_price

def search_buylist(term=None, race=None, type_=None):
    s = DbSession.factory()

    filters = []
    if race and race == "1":
        filters.append(Card.race.contains(term))
    if type_ and type_ == "1":
        filters.append(Card.type.contains(term))

    if term and filters:
        query = s.query(Card).filter(and_(Card.buylist == 1, or_(*filters) if len(filters) > 1 else filters[0]))
    else:
        query = s.query(Card).filter(Card.buylist == 1)

    # .order_by(Card.set_code) shows null set codes first
    result = list(query.filter(and_(Card.edition == '1st Edition',
                                    Card.condition == 'Near Mint')).limit(500))
    s.close()
    return result


def change_state(card_id, value, set_code):
    s = DbSession.factory()
    cards = s.query(Card).filter(and_(Card.card_id == card_id, Card.set_code == set_code)).all()
    if cards:
        data = {'msg': 'ok'}
        for card in cards:
            if int(value) == 0:
                card.buylist = 1
                data['class'] = 'fav_button_faved'
            else:
                card.buylist = 0
                data['class'] = 'fav_button'
            data['new'] = card.buylist
        s.commit()

    else:
        data = {'msg': 'fail'}
    s.close()
    return data


def make_html_from_results(result_list, request):
    html_all = ''
    for item in result_list:
        buy_cad = create_sell_price(item, 'CAD', True)
        buy_usd = create_sell_price(item, 'USD', True)
        avg_cad = "{:.2f}$".format(float(item.AVG_CAD_PRICE)) if item.AVG_CAD_PRICE else "-"
        avg_usd = "{:.2f}$".format(float(item.AVG_CAD_PRICE)) if item.AVG_CAD_PRICE else "-"

        set_code = item.set_code
        if set_code:
            rarity = item.set_rarity.lower().strip().replace(' ', '_')
            edition = item.edition.lower().strip().replace(' ', '_')
            img_name = "{}_{}_{}.jpg".format(set_code.lower().strip(), rarity, edition)
            alt_img_name = "{}_{}_{}.jpg".format(set_code.lower().strip(), rarity,
                                                 'unlimited' if edition != 'unlimited' else '1st_edition')
            image = request.static_url(
                'ygolegacy:static/img_ygo/{}'.format(img_name))
            alt_image = request.static_url(
                'ygolegacy:static/img_ygo/{}'.format(alt_img_name))
        else:
            image = None
            alt_image = None

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
        buylist_price = item.buylist_price if item.buylist_price else ""
        print(last_updated, item.id)
        html = f"""
                            <section class="sec1" id="{item.id}" >

                    <div class="container">
                    <div class="row">
                    <div class="col-sm-3 col-3">
                        <div class="imgg">
                    		<div class="img_hov">
                    		</div>
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

                        <form method="POST" action="/live/postEbay" enctype="multipart/form-data">
                        <input type="hidden" name="item_id" value="{item.id}">
                        <div>
                          

                        <div>
                          <input type="text" value="{buylist_price}" name="value">
                        
                        </div>
                        <!--<button type="submit" item-id="{item.id}" name="update_btn" value="price">Save Price</button>-->
        
                        <p style="color: white;">{"Inventory: " + str(item.YGOLEGACY_INVENTORY) if item.YGOLEGACY_INVENTORY else "Inventory: 0"}</p>
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