import json

from pyramid.response import Response
from pyramid.view import view_config

from ygolegacy.infrastructure import cookie_auth, request_dict
from ygolegacy.services import buylist_service, site_service


@view_config(route_name='buylist_result')
def search(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    term = data.term
    race = data.race
    type_ = data.type
    result_list = buylist_service.search_buylist(term=term, race=race, type_=type_)
    html = site_service.make_html_from_results(result_list, request, term)
    return Response(html)

@view_config(route_name='heart')
def change_card(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    card_id = data.id
    heart_value = data.heart_value
    set_code = None if data.set_code == "None" else data.set_code
    resp_data = buylist_service.change_state(card_id, heart_value, set_code)
    return Response(json.dumps(resp_data))


@view_config(route_name='wishlist',
             renderer='ygolegacy:templates/home/result.pt',
             request_method='GET')
@view_config(route_name='wishlist/',
             renderer='ygolegacy:templates/home/result.pt',
             request_method='GET')
def wishlist_get(request):
    # data = request_dict.create(request)
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))

    result_list = buylist_service.search_buylist()
    html = site_service.make_html_from_results(result_list, request, 'buylist')

    return {
        'user_id': user_id,
        'content': html,
        'search': True,
        'buylist': True,
        'ebay': False,
        'inventory': False,
        'main': False,
        'new_buylist': False
    }

@view_config(route_name='buylist',
             renderer='ygolegacy:templates/home/buylist.pt',
             request_method='GET')
@view_config(route_name='buylist/',
             renderer='ygolegacy:templates/home/buylist.pt',
             request_method='GET')
def buylist_get(request):
    data = request_dict.create(request)
    html = None
    if data.term:
        print(data.term)
        result_list = site_service.search_all(data.term)
        html = buylist_service.make_html_from_results(result_list, request)
    return {
        'user_id': cookie_auth.get_user_id_via_auth_cookie(request),
        'search': True,
        'content': html,
        'buylist': False,
        'ebay': False,
        'inventory': False,
        'new_buylist': True,
        'main': False
        }


@view_config(route_name='buyresult')
def search(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    term = data.term
    set_code = data.set_code
    result_list = site_service.search_all(term, set_code)
    html = buylist_service.make_html_from_results(result_list, request)
    return Response(html)