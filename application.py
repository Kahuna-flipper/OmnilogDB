from flask import Flask, render_template, url_for, jsonify
from flask import request
''' CONNECTING TO DATABASES '''
# MYSQL - for metadata
from ex_config import SQLALCHEMY_DATABASE_URI, MONGO_CNX
from sqlalchemy import create_engine
engine = create_engine(SQLALCHEMY_DATABASE_URI)
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

# Mongo for growth data
import pymongo
# Making a Connection with MongoClient
myclient = pymongo.MongoClient(MONGO_CNX['client'])
# database
mydb = myclient[MONGO_CNX['db']]
# collection
mongo_table= mydb[MONGO_CNX['collection']]
data = mongo_table.find()
from phenom_db import *
import pandas as pd





app = Flask(__name__,template_folder='templates',static_url_path='/static')

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


@app.route('/ecoli')
def ecoli():
    return render_template('ecoli.html')


@app.route('/strains/json', methods=['GET'])
def strains_json():
    print(request.args.get('name'))
    strain_data = pd.read_csv('./static/ecoli/metadata/summary.csv')

    out2 = []

    for i in strain_data.index:
        plateid = strain_data.loc[i,'PlateIDs']
        plate = strain_data.loc[i,'Plate']
        strain = strain_data.loc[i,'Strain']
        metadata = strain_data.loc[i,'Modification/Metadata']
        specie = strain_data.loc[i,'Specie']
        project = strain_data.loc[i,'Project ']
        poc = strain_data.loc[i,'POC']

        out2.append([
            str(plateid),
            str(plate),
            str(strain),
            str(metadata),
            str(specie),
            str(project),
            str(poc)])


    #return jsonify(data=out)
    return jsonify(data=out2)

@app.route('/projects/json', methods=['GET'])
def projects():
    project_data = pd.read_csv('./static/ecoli/metadata/project_summary.csv')
    out2 = []

    for i in project_data.index:
        project = project_data.loc[i,'Project']
        description = project_data.loc[i,'Description']

        out2.append([
            str(project),
            str(description)])


    #return jsonify(data=out)
    return jsonify(data=out2)


if __name__=="__main__":
    app.run(debug=True)