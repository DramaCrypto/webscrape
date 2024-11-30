import json

from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as x

from ygolegacy.infrastructure import request_dict, cookie_auth
from ygolegacy.services import site_service


@view_config(route_name='result')
def search(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    term = data.term
    set_code = data.set_code
    result_list = site_service.search_all(term, set_code)
    html = site_service.make_html_from_results(result_list, request, term)
    return Response(html)


@view_config(route_name='home',
             renderer='ygolegacy:templates/home/result.pt',
             request_method='GET')
@view_config(route_name='home/',
             renderer='ygolegacy:templates/home/result.pt',
             request_method='GET')
def home_get(request):
    data = request_dict.create(request)
    html = None
    if data.term:
        print(data.term)
        result_list = site_service.search_all(data.term)
        html = site_service.make_html_from_results(result_list, request, data.term)

    return {
        'user_id': cookie_auth.get_user_id_via_auth_cookie(request),
        'content': html,
        'search': True,
        'buylist': False,
        'ebay': False,
        'inventory': False,
        'new_buylist': False,
        'main': True
        }


@view_config(route_name='home',
             renderer='ygolegacy:templates/home/result.pt',
             request_method='POST')
@view_config(route_name='home/',
             renderer='ygolegacy:templates/home/result.pt',
             request_method='POST')
def home_post(request):
    data = request_dict.create(request)

    password = data.password

    if password:
        correct_password = site_service.login_user(password)
        if correct_password:
            cookie_auth.set_auth(request, 1)
        return x.HTTPFound('/live')

    term = data.search
    set_code_search = "1" if data.set_code_search else "0"

    html = None
    if term:
        user_id = cookie_auth.get_user_id_via_auth_cookie(request)
        if not user_id:
            return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
        result_list = site_service.search_all(term, set_code_search)
        html = site_service.make_html_from_results(result_list, request, term)

    return {
        'user_id': cookie_auth.get_user_id_via_auth_cookie(request),
        'content': html,
        'search': True,
        'buylist': False,
        'ebay': False,
        'inventory': False,
        'new_buylist': False,
        'main': True
    }



