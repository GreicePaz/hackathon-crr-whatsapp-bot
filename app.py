from flask import Flask, request, send_file
from flask_restful import request, abort
from twilio.twiml.messaging_response import MessagingResponse

from lib import utils
from os import path

import requests, json


app = Flask(__name__)

app.config.from_pyfile("local.cfg")


@app.route("/v1/bot", methods=['POST'])
def bot():
    message_values = request.values

    incoming_msg = message_values.get('Body', '').lower()
    print(message_values)
    resp = MessagingResponse()
    msg = resp.message()

    media_msg = message_values.get('MediaUrl0') if int(message_values.get('NumMedia')) > 0 else False

    if media_msg:
        name_audio = utils.download_audio(media_msg)

        if not name_audio:
            msg.body('Não entendi parceiro. Escreve ou manda áudio aí.')

            return str(resp)

        response = utils.convert_audio_in_text(name_audio)
        if not response.get('sucess'):
            msg.body('Não entendi parceiro. Escreve aí.')

            return str(resp)

        text_audio = response.get('text')
        params = {'phrase': text_audio}
        url = f'{app.config["URL_BACKEND"]}/recomendations/search'

        req = requests.get(url, params=params)
        try:
            req_json = req.json()
            if req.status_code != 200 or req_json.get('message'):
                msg.body('Não entendi parceiro. Tente pesquisar por: restaurante, comida, gasolina, posar')

                return str(resp)
        except:    
            msg.body('Não entendi parceiro. Tente pesquisar por: restaurante, comida, gasolina, posar')

            return str(resp)
        
        response = f'''Encontrei o seguinte local: {req_json.get('name')}\nLocalizado em: {req_json.get('address')}\nVer mais sobre: {req_json.get('link')}'''

        msg.body(response)

    else:
        result = any(elem in incoming_msg for elem in app.config['HELLO'])
        
        if result:
            introduction = app.config['INTRODUCTION']
            print(introduction)
            msg.body(introduction)
        else:
            retorno_audio = utils.convert_text_in_audio(incoming_msg)
            msg.body(f'static/{retorno_audio}')

    return str(resp)


@app.route("/v1/media", methods=['POST'])
def audio():
    data = request.form['phrase']

    if not data:
        abort(404, message='Parâmetros insuficientes')

    audio = f'static/{utils.convert_text_in_audio(data)}'

    return send_file(audio)


@app.route("/", methods=['GET'])
def init_app():
    return {'sucess': True}


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])