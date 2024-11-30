import json
from pprint import pprint

from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as x

from ygolegacy.data.cards import Card
from ygolegacy.infrastructure import cookie_auth, request_dict
from ygolegacy.services import ebay_services, site_service, ebay_api_services, calc_service


def cors_headers(request, response):
    response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
        'Content-Type': 'application/json'
    })


@view_config(route_name='post_ebay')
def post_ebay(request: Request):
    # request.add_response_callback(cors_headers)
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    pprint(data)

    group_id = data.ebay_page

    button = data.update_btn
    if button == 'delete':
        if data.ebay_id:
            ebay_api_services.delete_item(data.ebay_id)
            return x.HTTPFound('/live/ebay?group={}'.format(group_id))
        return Response(json.dumps({'message': "no ebay id"}))

    value_type = data.valueType
    playset = data.playset
    presale = data.presale
    image = data.image
    image_url = data.image_url
    img_url_prefix = request.static_url("ygolegacy:static/ebay_image")

    print('playset ', playset, ' presale ', presale)

    # Todo ADD modelview
    if (value_type == "%" or value_type == '$') and data.value:
        value = float(data.value.replace('$',''))
        item_id = data.item_id
        ebay_services.post_ebay_product(item_id, value, value_type, image, img_url_prefix, playset, presale, button, image_url)
        return x.HTTPFound(f'/live/ebay?group={group_id}#{item_id}')
    print('value type', value_type)

    return Response(json.dumps({'message': "incorrect parameters"}))


# 1 Group 10$+
# 1 Group 4$+ to 9.99$
# 1 group 0.95$ to 3.99$
# 1 Group 0.00$ to 0.94$


@view_config(route_name='ebay',
             renderer='ygolegacy:templates/home/ebay.pt',
             request_method='GET')
@view_config(route_name='ebay/',
             renderer='ygolegacy:templates/home/ebay.pt',
             request_method='GET')
def ebay_get(request):
    data = request_dict.create(request)
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))

    ebay_group = int(data.group)
    result_list = ebay_services.get_ebay_for_group(ebay_group)
    groups = {
        0: 'No Price', 1: '10$+', 2: '4$-9.99$', 3: '4$-9.99$', 4: '2$-3.99$', 5: '2$-3.99$', 6: '2$-3.99$'
    }
    for idx in range(7, 26):
        groups[idx] = str(idx - 3)
    title = groups[ebay_group]
    html = ebay_services.make_html_from_results(result_list, request, str(ebay_group))

    # if data.m and data.m == "-":
    #     # read results from pickle result_list = ebay_services.get_above_10_avg(True)
    #     result_list = [Card(**c) for c in calc_service.read_pickle('ebay10') if ''][:1000]
    #     title = "$10-"
    #     html = ebay_services.make_html_from_results(result_list, request, "+" if title == "$10+" else "-")
    # else:
    #     result_list = ebay_services.get_above_10_avg()
    #     title = "$10+"
    #     html = ebay_services.make_html_from_results(result_list, request, "+" if title == "$10+" else "-")
    return {
        'user_id': user_id,
        'content': html,
        'search': False,
        'ebay': True,
        'title': title,
        'new_buylist': False,
        'main': False
    }


@view_config(route_name='ebay_ind',
             request_method='GET',
             renderer='ygolegacy:templates/home/ebay.pt',)
def ebay_ind_get(request):
    data = request_dict.create(request)
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))

    card_id = data.card_id
    card = ebay_services.find_card_by_id(card_id)
    if not card:
        return Response(status=400, body='no card id {}'.format(card_id))
    result_list = [card]
    html = ebay_services.make_html_from_results(result_list, request, '1')

    return {
        'user_id': user_id,
        'content': html,
        'search': False,
        'ebay': True,
        'title': card.set_code,
        'new_buylist': False,
        'main': False
    }