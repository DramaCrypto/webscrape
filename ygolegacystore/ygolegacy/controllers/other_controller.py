import os

from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='images',
             request_method='GET')
def images(request):
    try:
        images = os.listdir('/apps/app_repo/ygolegacy/ygolegacy/static/img_ygo')
    except Exception as e:
        return Response(status=400, json_body={'error': str(e)})

    # Filter out
    img_resp = {}
    track = []
    for img in images:
        code = img.split('_')[0]
        if code in track:
            continue
        else:
            img_resp[code.lower()] = img
            track.append(code)

    return Response(status=200, json_body={'images': img_resp})