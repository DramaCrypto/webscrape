from pyramid.config import Configurator

from ygolegacy.data.db_session import DbSession


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    init_includes(config)
    init_db(config)
    init_routing(config)

    return config.make_wsgi_app()


def init_includes(config):
    config.include('pyramid_chameleon')


def init_routing(config):
    config.add_static_view('static', 'static', cache_max_age=3600)

    # home controller
    config.add_route('home', '/live')
    config.add_route('home/', '/live/')

    # calculator pages controllers
    config.add_route('binder', '/live/binder-value')
    config.add_route('stock', '/live/stock-inventory')

    # top 100 page controllers

    # Wishlist page controllers
    config.add_route('wishlist', '/live/wishlist')
    config.add_route('wishlist/', '/live/wishlist/')
    config.add_route('buylist_result', '/live/buylist-result')

    # Buylist page controllers
    config.add_route('buylist', '/live/buylist')
    config.add_route('buylist/', '/live/buylist/')
    config.add_route('buyresult', '/live/buylist/result')

    # ebay page controllers
    config.add_route('ebay', '/live/ebay')
    config.add_route('ebay/', '/live/ebay/')
    config.add_route('ebayResult', '/live/ebayResult')
    config.add_route('post_ebay', '/live/postEbay')

    # enter inventory page
    config.add_route('enter_inventory', '/live/enterInventory')
    config.add_route('enter_inventory/', '/live/enterInventory/')

    # api endpoints controllers
    config.add_route('result', '/live/result')
    config.add_route('result_inv', '/live/resultInv')
    config.add_route('inventory', '/live/inventory')

    config.add_route('cards', 'live/cards')

    config.add_route('heart', 'live/heart')

    # trending/top100/marketwatch
    config.add_route('top100', '/live/top100')
    config.add_route('top100/', '/live/top100/')
    config.add_route('trending', '/live/trending')
    config.add_route('trending/', '/live/trending/')
    config.add_route('marketwatch', '/live/marketwatch')
    config.add_route('marketwatch/', '/live/marketwatch/')

    config.add_route('card_details', '/live/card/details/{card_id}')

    # Other
    config.add_route('images', '/api/images')

    # Ebay individual
    config.add_route('ebay_ind', '/live/ebay/item/{card_id}')

    config.scan()


def init_db(_):
    DbSession.global_init()
