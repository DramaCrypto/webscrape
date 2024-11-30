from sqlalchemy import and_, or_

from ygolegacy import DbSession
from ygolegacy.data.cards import Card

def mke_html_from_results(result_list):
    html_all = """
    <style>
    table, th, td {
      border: 1px solid black;
    }
    #inventory_table  th{
    color: gray;
    }
    #inventory_table  td{
    color: black;
    background-color: white;
    }
    </style>
    <div class='container'>
    <table id='inventory_table' style='width:100%;'>
    <tr>
    <th>Name</th>
    <th>Set Code</th>
    <th>Set Rarity</th>
    <th>Edition</th>
    <th>Condition</th>
    <th>Inventory</th>
  </tr>"""
    for card in result_list:
        html_all += f"""<tr>
            <td>{card.name}</td>
            <td>{card.set_code}</td>
            <td>{card.set_rarity}</td>
            <td>{card.edition}</td>
            <td>{card.condition}</td>
            <td><input style='width:100%;' type='text' onchange='updateInventory(this);' class='enter_inventory' id='{card.id}' value='{int(card.YGOLEGACY_INVENTORY) if card.YGOLEGACY_INVENTORY else 0}'></td>
        </tr>"""
    html_all += '</table></div>'
    return html_all


def search_all(term, set_code):
    s = DbSession.factory()

    if not set_code or set_code == "0":
        if len(term) <= 2:
            return []
        query = s.query(Card).filter(and_(
            Card.name.contains(term),
            or_(Card.condition == "Near Mint",
                Card.condition == 'Slightly Played')
        ))
        query = query.order_by(Card.name)
    elif set_code and set_code == '1':
        if len(term) <= 3:
            return []

        query = s.query(Card).filter(
            and_(
                Card.set_code.startswith(term),
                or_(Card.condition == "Near Mint",
                    Card.condition == 'Slightly Played')
            ))
        query = query.order_by(Card.set_code)
        codes = [x.set_code for x in query]
        print(codes)

    result = list(query.all())
    s.close()
    return result
