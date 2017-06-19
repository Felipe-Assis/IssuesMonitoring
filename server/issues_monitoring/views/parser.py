import sqlite3
from flask import request
from .. import app, Config, controllers

@app.route('/parser', methods=['POST'])
def parser():
    json = request.get_json()
    if json is not None:
        try:
            if json['token'] == Config.token_parser:
                controllers.registrar_presenca(json['data'])
                controllers.registrar_log_parser()
            else:
                return "-1"
        except sqlite3.Error:
            return "-2"
        except KeyError:
            pass
    else:
        print("Couldn't get json from POST request. Update only the report time")
        controllers.registrar_log_parser()
    return str(controllers.obter_intervalo_parser())
