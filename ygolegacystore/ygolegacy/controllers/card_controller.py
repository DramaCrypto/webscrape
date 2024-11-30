import json

from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as x

from ygolegacy import DbSession
from ygolegacy.data.cards import Card
from ygolegacy.infrastructure import request_dict, cookie_auth
from ygolegacy.services import site_service


@view_config(route_name='inventory')
def add_inventory(request):
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return Response(json.dumps({'message': "you have to be logged in to access this endpoint"}))
    data = request_dict.create(request)
    s = DbSession.factory()
    try:
        matched_card = s.query(Card).filter(Card.id == data.card_id).one()
    except:
        matched_card = None

    if not matched_card:
        return Response(json.dumps({'message': "Can't find row with that id"}))
    else:
        new_value = int(data.new_value)
        matched_card.YGOLEGACY_INVENTORY = new_value
        s.commit()
    s.close()

    return Response(json.dumps({'message': 'Inventory changed successfully'}))
#
# @view_config(route_name='card',
#              renderer='ygolegacy:templates/home/card.pt')
# @view_config(route_name='card/',
#              renderer='ygolegacy:templates/home/card.pt')
# def card_page(request: Request):
#     user_id = cookie_auth.get_user_id_via_auth_cookie(request)
#     if not user_id:
#         return x.HTTPFound('/')
#     data = request_dict.create(request)
#     edition_id = data.edition_id
#     term = data.term
#     cards = site_service.find_card_conditions(edition_id)
#     return {'cards': cards, 'user_id': user_id, 'term': term, 'search': True}