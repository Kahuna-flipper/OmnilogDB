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
from scripts import scripts





app = Flask(__name__,template_folder='templates',static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


@app.route('/species', methods=['GET'])
def species():
    specie = request.args.get('specie')
    #print(specie)
    #specie = 'ecoli'
    return render_template('species.html',specie=specie)


@app.route('/strains/json', methods=['GET'])
def strains_json():
    strain = request.args.get('strain')
    strain_data = pd.read_csv('./static/'+strain+'/metadata/summary.csv')

    out2 = []

    for i in strain_data.index:
        plateid = strain_data.loc[i,'PlateIDs']
        plate = strain_data.loc[i,'Plate']
        strain = strain_data.loc[i,'Strain']
        metadata = strain_data.loc[i,'Modification/Metadata']
        specie = strain_data.loc[i,'Specie']
        project = strain_data.loc[i,'Project']
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
    strain = request.args.get('strain')
    project_data = pd.read_csv('./static/'+strain+'/metadata/project_summary.csv')
    out2 = []

    for i in project_data.index:
        project = project_data.loc[i,'Project']
        description = project_data.loc[i,'Description']

        out2.append([
            str(project),
            str(description)])


    #return jsonify(data=out)
    return jsonify(data=out2)
    

@app.route('/dashboard/strains', methods=['GET'])
def dashboard_strains():

    total_strains = strain.strain_summary()
    strain = request.args.get('strain')
    strain_data = pd.read_csv('./static/'+strain+'/metadata/summary.csv')

    out2 = []

    for i in total_strains.index:
        num_specie = total_strains.loc[i,'Num Strains']
        specie = i

        out2.append([
            str(specie),
            str(num_specie),])


    #return jsonify(data=out)
    return jsonify(data=out2)

if __name__=="__main__":
    app.run(debug=True)