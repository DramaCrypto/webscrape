import json

import requests
from pyramid.response import Response
from pyramid.view import view_config

from ygolegacy.infrastructure import cookie_auth, request_dict
from ygolegacy.services import top100_services


@view_config(route_name='trending',
             renderer='ygolegacy:templates/home/top100.pt',
             request_method='GET')
@view_config(route_name='trending/',
             renderer='ygolegacy:templates/home/top100.pt',
             request_method='GET')
def trending_get(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    hours = int(data.hours) if data.hours else 24
    result_list = top100_services.get_top_sold(hours)
    html = top100_services.make_html_from_results(result_list, request)

    return {
        'user_id': user_id,
        'content': html,
        'search': False,
        'buylist': False,
        'ebay': False,
        'hours': hours,
        'title': 'Trending',
        'endpoint': '/live/trending',
        'new_buylist': False
    }


@view_config(route_name='top100',
             renderer='ygolegacy:templates/home/top100.pt',
             request_method='GET')
@view_config(route_name='top100/',
             renderer='ygolegacy:templates/home/top100.pt',
             request_method='GET')
def top100_get(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    hours = int(data.hours) if data.hours else 24
    auth = {'Authorization': 'api-key: 119fa586-abde-46bd-8b97-944e8fcfd8df'}
    result_list = requests.get(f'https://api.ygotrader.com/api/top100?hours={hours}', timeout=60, headers=auth)
    #print(result_list.json())
    html = top100_services.make_html_for_top100(result_list.json())

    return {
        'user_id': user_id,
        'content': html,
        'search': False,
        'buylist': False,
        'ebay': False,
        'hours': hours,
        'title': 'Top100',
        'endpoint': '/live/top100',
        'new_buylist': False
    }

@view_config(route_name='marketwatch',
             renderer='ygolegacy:templates/home/top100.pt',
             request_method='GET')
@view_config(route_name='marketwatch/',
             renderer='ygolegacy:templates/home/top100.pt',
             request_method='GET')
def marketwatch_get(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    hours = int(data.hours) if data.hours else 24
    auth = {'Authorization': 'api-key: 119fa586-abde-46bd-8b97-944e8fcfd8df'}
    result_list = requests.get(f'https://api.ygotrader.com/api/marketwatch?hours={hours}', timeout=60, headers=auth)
    html = top100_services.make_html_for_marketwatch(result_list.json())

    return {
        'user_id': user_id,
        'content': html,
        'search': False,
        'buylist': False,
        'ebay': False,
        'hours': hours,
        'title': 'MarketWatch',
        'endpoint': '/live/marketwatch',
        'new_buylist': False,
        'main': False
    }


@view_config(route_name='card_details',
             renderer='ygolegacy:templates/home/details.pt',
             request_method='GET')
def card_details_get(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    card_id = request.matchdict.get('card_id')
    content = top100_services.make_html_for_details(card_id, request)
    return {
        'user_id': user_id,
        'search': False,
        'buylist': False,
        'ebay': False,
        'content': content,
        'new_buylist': False,
        'main': False
    }