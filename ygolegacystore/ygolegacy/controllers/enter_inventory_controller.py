import json

from pyramid.response import Response
from pyramid.view import view_config

from ygolegacy.infrastructure import request_dict, cookie_auth
from ygolegacy.services import site_service, enter_inventory_service


@view_config(route_name='result_inv')
def search(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    term = data.term
    set_code = data.set_code
    result_list = enter_inventory_service.search_all(term, set_code)
    print(result_list)
    html = enter_inventory_service.mke_html_from_results(result_list)
    return Response(html)

@view_config(route_name='enter_inventory',
             renderer='ygolegacy:templates/home/inventory.pt',
             request_method='GET')
@view_config(route_name='enter_inventory/',
             renderer='ygolegacy:templates/home/inventory.pt',
             request_method='GET')
def enter_inventory_get(request):
    data = request_dict.create(request)
    return {
        'user_id': cookie_auth.get_user_id_via_auth_cookie(request),
        'search': True,
        'buylist': False,
        'ebay': False,
        'inventory': True,
        'new_buylist': False,
        'main': False
        }
