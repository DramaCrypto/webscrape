from datetime import datetime, timedelta
import operator

from ygolegacy import DbSession
from ygolegacy.services.site_service import create_sell_price
from ygolegacy.data.cards import Card
from ygolegacy.data.top100 import SoldCard


def get_top_sold(hours: int):
    session = DbSession.factory()
    since = datetime.now() - timedelta(hours=hours)
    sold_cards = session.query(SoldCard).filter(SoldCard.sold_date > since).all()
    session.close()
    data = {}
    dates_data = {}
    names_data = {}
    ids_data = {}
    for card in sold_cards:
        names_data[card.set_code] = card.name
        if card.set_code not in data.keys():
            data[card.set_code] = 1
        else:
            data[card.set_code] += 1
        if card.set_code not in dates_data.keys():
            dates_data[card.set_code] = ["Sold on {} for {}".format(card.sold_date, card.price)]
            ids_data[card.set_code] = [card.id]
        else:
            dates_data[card.set_code].append("Sold on {} for ${}".format(card.sold_date, card.price))

    sorted_x = sorted(data.items(), key=operator.itemgetter(1))
    sorted_x.reverse()
    final = []
    for x in sorted_x:
        final.append((x[0], x[1], names_data[x[0]], dates_data[x[0]], ids_data[x[0]]))
    print(final)
    return final


def make_html_from_results(result_list, request):
    html_all = ''
    for item in result_list:
        # set_code = item.set_code
        # if set_code:
        #     rarity = item.set_rarity.lower().strip().replace(' ', '_')
        #     edition = item.edition.lower().strip().replace(' ', '_')
        #     img_name = "{}_{}_{}.jpg".format(item[0].lower().strip(), rarity, edition)
        #     image = request.static_url(
        #         'ygolegacy:static/img_ygo/{}'.format(img_name))
        # else:
        #     image = ''

        # image = 'http://167.114.68.171/static/image/{}.jpg'.format(item[0].upper())
        opts = ''.join(["<option>{}</option>".format(x) for x in item[3]])
        html = f"""
                            <section class="sec1" >
                    <div class="container">
                    <div class="row">
                    <div class="col-sm-3 col-3">
                      
                    </div>
                    <div class="col-sm-6 col-7">
                    <div class="main-middle">
                    <div class="middle_content">
                    <h2>{item[2]} - {item[0]}</h2>
                    <label for="{item[0]}">Sold on:</label>
                        <select class="form-control" id="{item[0]}" multiple>
                          {opts}
                        </select>
            

                    </div>
                    <div class="bottm_content">
                    <div class="row">
                    <div class="col-sm-4 col-4">
                    
                    </div>  
                    <div class="col-sm-4 col-4">
                   
                    </div>
                    <div class="col-sm-4 col-4">
                   
                    </div>
                    </div>

                    </div>
                    </div>

                

                    </div>
                    <div class="col-sm-3 col-2">
                    <div class="rght_bx">
                    <h3> Sold: {item[1]}</h3>


                    </div>
                    </div>
                    </div>
                    </div>
                    </section>
                            """
        html_all += html
    return html_all


def make_html_for_marketwatch(result_list):
    html_all = ''
    for item in result_list:
        # set_code = item.set_code
        # if set_code:
        #     rarity = item.set_rarity.lower().strip().replace(' ', '_')
        #     edition = item.edition.lower().strip().replace(' ', '_')
        #     img_name = "{}_{}_{}.jpg".format(item[0].lower().strip(), rarity, edition)
        #     image = request.static_url(
        #         'ygolegacy:static/img_ygo/{}'.format(img_name))
        # else:
        #     image = ''

        # image = 'http://167.114.68.171/static/image/{}.jpg'.format(item[0].upper())

        html = f"""
                            <section class="sec1" >
                    <div class="container">
                    <div class="row">
                    <div class="col-sm-3 col-3">
                    </div>
                    <div class="col-sm-6 col-7">
                    <h4 style="color: #D1AA42;">Rank {item['rank']}</h4>
                    <div class="main-middle">
                    <div class="middle_content">
                    <h2>{item['cardDetails']['name']} - {item['cardDetails']['setCode']}</h2>
                    <ul>
                        <li>{item['cardDetails']['rarity']}</li>
                        <li>{item['cardDetails']['edition']}</li>
                    </ul>


                    </div>
                    <div class="bottm_content">
                    <div class="row">
                    <div class="col-sm-4 col-4">

                    </div>  
                    <div class="col-sm-4 col-4">

                    </div>
                    <div class="col-sm-4 col-4">

                    </div>
                    </div>

                    </div>
                    </div>



                    </div>
                    <div class="col-sm-3 col-2">
                    <div class="rght_bx">
                    <h3 style="font-size: 220%;">{"{:.2f}".format(item['fluctuation'])}%</h3>
                    <h3 style="font-size: 220%;">{"{:.2f}".format(item['price'])}$</h3>
                    <a href="/live/card/details/{item['id']}" style="color: #D1AA42"> <i class="fa fa-arrow-right"></i></a>


                    </div>
                    </div>
                    </div>
                    </div>
                    </section>
                            """
        html_all += html
    return html_all


def make_html_for_top100(result_list):
    html_all = ''
    for item in result_list:
        # set_code = item.set_code
        # if set_code:
        #     rarity = item.set_rarity.lower().strip().replace(' ', '_')
        #     edition = item.edition.lower().strip().replace(' ', '_')
        #     img_name = "{}_{}_{}.jpg".format(item[0].lower().strip(), rarity, edition)
        #     image = request.static_url(
        #         'ygolegacy:static/img_ygo/{}'.format(img_name))
        # else:
        #     image = ''

        # image = 'http://167.114.68.171/static/image/{}.jpg'.format(item[0].upper())

        html = f"""
                            <section class="sec1" >
                    <div class="container">
                    <div class="row">
                    <div class="col-sm-3 col-3">
                    </div>
                    <div class="col-sm-6 col-7">
                    <h4 style="color: #D1AA42;">Rank {item['rank']}</h4>
                    <div class="main-middle">
                    <div class="middle_content">
                    <h2>{item['cardDetails']['name']} - {item['cardDetails']['setCode']}</h2>
                    <ul>
                        <li>{item['cardDetails']['rarity']}</li>
                        <li>{item['cardDetails']['edition']}</li>
                    </ul>
                  

                    </div>
                    <div class="bottm_content">
                    <div class="row">
                    <div class="col-sm-4 col-4">

                    </div>  
                    <div class="col-sm-4 col-4">

                    </div>
                    <div class="col-sm-4 col-4">

                    </div>
                    </div>

                    </div>
                    </div>



                    </div>
                    <div class="col-sm-3 col-2">
                    <div class="rght_bx">
                    <h3 style="font-size: 220%;"> Price: {"{:.2f}$".format(item['price'])}</h3>
                    <a href="/live/card/details/{item['id']}" style="color: #D1AA42"> <i class="fa fa-arrow-right"></i></a>


                    </div>
                    </div>
                    </div>
                    </div>
                    </section>
                            """
        html_all += html
    return html_all


def make_html_for_details(card_id: int, request) -> str:
    session = DbSession.factory()
    item = session.query(Card).filter(Card.id == card_id).first()
    if not item:
        return f"<section><h2>No card with id: {card_id}</h2></section>"

    buy_cad = create_sell_price(item, 'CAD', True)
    buy_usd = create_sell_price(item, 'USD', True)
    # image = request.static_url(
    #     'ygolegacy:static/image/{}.jpg'.format(item.set_code.upper())) if item.set_code else ''
    # image = ""  # TODO

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
    # image =''
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

    return f"""
                    <section class="sec1" id="{item.id}" >
            <div class="container">
            <div class="row">
            <div class="col-sm-3 col-3">
                <div class="imgg">
            		<div class="img_hov">
            			<p class="buy_cad">{buy_cad}<span>CAD</span></p>
            			<p class="buy_usd">{buy_usd}<span>USD</span></p>
            		</div>
            		<img src="{image}" onerror="this.onerror=null;this.src='{alt_image}';" class="img-fluid" alt="img1">
            	</div>
            </div>
            <div class="col-sm-6 col-7">
            <div class="main-middle">
            <div class="middle_content">
            <h2>{item.name if item.name else 'null'} <a onclick="heartCard(this);" class="{'fav_button' if item.buylist == 0 else 'fav_button_faved'}" value="{item.buylist}" item-id="{item.card_id}" uid="{item.id}" ><i class="fa fa-heart"></i></a> </h2>
            <ul>
                <li>{item.set_name if item.set_name else 'None'}</li>
                <li>{item.set_rarity if item.set_rarity else 'None'}</li>
                <li class="set_code">{item.set_code if item.set_code else 'None'}</li>
                <li class="edition">{item.edition if item.edition else 'null'}</li>
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

                <a  class="increment" style="color: #D1AA42" data-id="{item.id}" onclick="updateValue(this);" update-type="increment"> <i class="fa fa-plus"></i></a>
                <h3>INVENTORY</h3>
                <h5 id="inv-{item.id}">{item.YGOLEGACY_INVENTORY if item.YGOLEGACY_INVENTORY else 0}</h5>
                <a class="decrement" style="color: #D1AA42" data-id="{item.id}" onclick="updateValue(this);" update-type="decrement"> <i class="fa fa-minus"></i></a>

            </div>
            </div>
            </div>
            </div>
            </section>
                    """




def round_price(price):
    if .01 <= price <= .50:
        price = .25
    elif .51 <= price <= .99:
        price = .95
    else:
        price = float(int(price)) + .95
    return price
