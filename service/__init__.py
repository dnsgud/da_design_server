
from flask import Flask, request, render_template
from flask_cors import CORS
from bson import json_util
import datetime
import os
from da_design_server.src import mylogger, myconfig, mydb
import pdb

app = Flask(__name__)
CORS(app)

# create a logger.
project_root_path = os.getenv("DA_DESIGN_SERVER")
cfg = myconfig.get_config('{}/share/project.config'.format(
    project_root_path))
log_directory = cfg['logger'].get('log_directory')
logger = mylogger.get_logger('app', log_directory)
db = mydb.mydb(cfg)

@app.route('/')
def web_main():
    return render_template("index.html")

@app.route('/help')
def web_help():
    return render_template("help.html")

@app.route('/list')
def web_list():
    ret = get_list_topk(10)
    ret_json = json_util.dumps(ret, ensure_ascii=False)
    return render_template("list.html",
        list_info=ret_json)

def get_list_topk(topk):
    today_date = datetime.datetime.now()
    result = db.get_company_value_of_date(today_date, topk)
    return result
@app.route('/api-list', methods=["POST"])
def api_list():
    top_k = request.json.get('top_k')
    logger.info('> API:list with {}'.format(top_k))

    ret = {"result": None, "msg": ""}
    if top_k:
        top_k = int(top_k)
        result = get_list_topk(top_k)
        if result:
            ret["result"] = result
        else:
            ret['msg'] = '결과값 생성에 실패하였습니다.'
    else:
        ret['msg'] = 'top_k 값이 주어져있지 않습니다.'

    logger.info('< API:list with {}'.format(ret))
    return ret

@app.route('/api-predict', methods=["POST"])
def api_predict():
    company_name = request.json.get('company_name')
    logger.info('> API:predict with {}'.format(company_name))

    ret = {"result": None, "msg": ""}
    if company_name:
        result = db.get_predicted_company_stock(company_name, logger)
        if result:
            ret["result"] = result
            ret['msg'] = company_name
        else:
            ret['msg'] = '결과값 생성에 실패하였습니다.'
    else:
        ret['msg'] = 'company_name 값이 주어져있지 않습니다.'

    logger.info('< API:list with {}'.format(ret))
    return ret
