# Pricing module config information

Welcome_Msg = 'Welcome to BitSeller!\n\n' + \
                  "This is an AUTOMATED service. Please follow instructions correctly otherwise your payment " \
                  "will not be processed and you will have to wait for an agent to assist.\n\n" + \
                  "We do not accept payments from MONZO or Pockit.\n\n" + \
                  "We are the UK's #1 broker for BTC.\n\n" + \
                  "--> Fully automated. Release of BTC in 2 mins.\n" + \
                  "--> Reliable and cheap trades.\n" + \
                  "--> Please do not use TOR / VPN.\n\n" + \
                  "OTC trades are available for 50,000+ trades, please enquire for a quote on the website.\n\n" + \
                  "Regards,\n" + \
                  "BitSeller Team'"

Sell_Url_Params = {
                    "price_equation": 'btc_in_usd*USD_in_GBP*1.100000',
                    "lat": 0,
                    "lon": 0,
                    "city": "London",
                    "location_string": "London City",
                    "countrycode": "gb",
                    "currency": "GBP",
                    "account_info": "-",
                    "bank_name": "UK Bank",
                    "msg": Welcome_Msg,
                    "sms_verification_required": False,
                    "track_max_amount": False,
                    "require_trusted_by_advertiser": False,
                    "require_identification": True,
                    "online_provider": "NATIONAL_BANK",
                    "trade_type": "ONLINE_SELL",
                    "min_amount": 1,
                    "max_amount": 4000,
                    "visible": True,
                    "require_feedback_score": 0
                }

Api_Base_Url = 'https://localbitcoins.com'

AD_Price_Low_Limit = 100
AD_Price_High_Limit = 220
AD_Price_Delta = 2
