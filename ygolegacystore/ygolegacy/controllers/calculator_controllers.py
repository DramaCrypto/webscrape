import json

from pyramid.response import Response
from pyramid.view import view_config

from ygolegacy.services import calc_service
from ygolegacy.infrastructure import cookie_auth, request_dict


@view_config(route_name='binder',
             renderer='ygolegacy:templates/home/calc.pt',
             request_method='GET')
def binder_get(request):
    data = request_dict.create(request)
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))

    if data.currency:
        card_data = calc_service.get_calc_page('value_{}'.format(data.currency.lower()))
    else:
        card_data = calc_service.get_calc_page('value_usd')


    return {
        'user_id': cookie_auth.get_user_id_via_auth_cookie(request),
        'search': False,
        'data': card_data,
        'cats': ['rarity_ordered', 'types_ordered', 'races_ordered',
                 'spell_ordered', 'trap_ordered', 'skill_ordered'],
        'value': True
    }


@view_config(route_name='stock',
             renderer='ygolegacy:templates/home/calc.pt',
             request_method='GET')
def stock_get(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))

    card_data = calc_service.get_calc_page('stock')

    return {
        'user_id': cookie_auth.get_user_id_via_auth_cookie(request),
        'search': False,
        'data': card_data,
        'cats': ['rarity_ordered', 'types_ordered', 'races_ordered',
                 'spell_ordered', 'trap_ordered', 'skill_ordered'],
        'value': False
    }