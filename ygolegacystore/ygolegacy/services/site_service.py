from sqlalchemy import or_, and_

from ygolegacy.data.cards import Card
from ygolegacy.data.db_session import DbSession
from ygolegacy.db_config import WEBSITE_PASSWORD


def login_user(password: str):
    return True if password == WEBSITE_PASSWORD else False


def search_all(term, set_code):
    s = DbSession.factory()

    if set_code == "0":
        if len(term) <= 2:
            return []
        query = s.query(Card).filter(
            and_(
                #or_(Card.edition == '1st Edition', Card.edition == 'Limited Edition'),
                 Card.condition == 'Near Mint',
                 Card.name.contains(term),
                 ))
        query = query.order_by(Card.name)
    elif set_code == '1':
        if len(term) <= 3:
            return []

        query = s.query(Card).filter(
            and_(
                #or_(Card.edition == '1st Edition', Card.edition == "Limited Edition"),
                 Card.condition == 'Near Mint',
                 Card.set_code.startswith(term),
                 ))
        query = query.order_by(Card.set_code)

    result = list(query.limit(500))
    s.close()
    return result


def find_card_conditions(edition_id):
    session = DbSession.factory()
    result = session.query(Card).filter(Card.edition_id == edition_id).all()
    session.close()
    return result


"""
<ul>
            
            """


def make_html_from_results(result_list, request, term):
    html_all = ''
    for item in result_list:
        buy_cad = create_sell_price(item, 'CAD', True) #"{:.2f}$".format(float(item.BUY_CAD_PRICE_75)) if item.BUY_CAD_PRICE_75 else "-"
        buy_usd = create_sell_price(item, 'USD', True)#"{:.2f}$".format(float(item.BUY_USD_PRICE_75)) if item.BUY_CAD_PRICE_75 else "-"
        # image = request.static_url(
        #     'ygolegacy:static/image/{}.jpg'.format(item.set_code.upper())) if item.set_code else ''
        # image = ""  # TODO

        set_code = item.set_code
        if set_code:
            rarity = item.set_rarity.lower().strip().replace(' ', '_')
            edition = item.edition.lower().strip().replace(' ', '_')
            img_name = "{}_{}_{}.jpg".format(set_code.lower().strip(), rarity, edition)
            alt_img_name = "{}_{}_{}.jpg".format(set_code.lower().strip(), rarity, 'unlimited' if edition != 'unlimited' else '1st_edition')
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

        # + "<small> ({}) </small>".format("-")
        if item.edition == 'Limited Edition':
            select_box = "<option>Limited Edition</option>"
        else:
            select_box = """<option value="">1st Edition</option>
<option value="">Unlimited</option>"""

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
            <h2>{item.name + " ({}CAD {}USD)".format(buy_cad, buy_usd) if item.name else 'null'} <a onclick="heartCard(this);" class="{'fav_button' if item.buylist == 0 else 'fav_button_faved'}" value="{item.buylist}" item-id="{item.card_id}" uid="{item.id}" ><i class="fa fa-heart"></i></a> </h2>
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
            
            <div style="margin: auto;">
                <select class="browser-default custom-select" card-id="{item.card_id}" item-id="{item.id}" id="edit{item.id}" onchange="selectEdition(this)">
                    {select_box}
                </select>
                <select class="browser-default custom-select" card-id="{item.card_id}" item-id="{item.id}" id="cond{item.id}" onchange="selectCondition(this)">
                    <option>Near Mint</option>
                    <option>Slightly Played</option>
                    <option>Moderately Played</option>
                    <option>Heavily Played</option>
                </select>
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
        html_all += html
    return html_all


def create_sell_price(card, currency, buy=False):
    currency_dict = {
        'CAD': card.ebayca_avg_cad_low,
        'USD': card.ebayca_avg_usd_low
    }
    backup_dict = {
        "CAD": card.TCGPLAYER_CAD_PRICE,
        'USD': card.TCGPLAYER_USD_PRICE
    }
    price = currency_dict[currency]
    if not price:
        price = backup_dict[currency]
        if not price:
            return "---"
        price = price * 1.25
    price = round_price(price)
    return "{0:.2f}".format(price * 0.6) if buy else price

def round_price(price):
    if .01 <= price <= .50:
        price = .25
    elif .51 <= price <= .99:
        price = .95
    else:
        price = float(int(price)) + .95
    return price
