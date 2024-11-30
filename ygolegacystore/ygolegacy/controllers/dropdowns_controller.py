import json

from pyramid.response import Response
from pyramid.view import view_config

from ygolegacy.infrastructure import cookie_auth, request_dict
from ygolegacy.services import dropdown_service


@view_config(route_name='cards')
def change_card(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    card_id = data.card_id
    condition = data.cond
    edition = data.edit
    set_code = data.code
    card = dropdown_service.get_card(card_id, edition, condition, set_code)
    if not card:
        card = {'msg': 'fail'}
    return Response(json.dumps(card))