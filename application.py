from flask import Flask, render_template, url_for, jsonify
from flask import request
''' CONNECTING TO DATABASES '''
# MYSQL - for metadata
#from ex_config import SQLALCHEMY_DATABASE_URI, MONGO_CNX
#from sqlalchemy import create_engine
#engine = create_engine(SQLALCHEMY_DATABASE_URI)
#from sqlalchemy.orm import sessionmaker
#Session = sessionmaker(bind=engine)
#session = Session()

# Mongo for growth data
#import pymongo
# Making a Connection with MongoClient
#myclient = pymongo.MongoClient(MONGO_CNX['client'])
# database
#mydb = myclient[MONGO_CNX['db']]
# collection
#mongo_table= mydb[MONGO_CNX['collection']]
#data = mongo_table.find()
#from phenom_db import *
import pandas as pd
import scripts





app = Flask(__name__,template_folder='templates',static_url_path='/static')

@app.route('/')
@app.route('/index')
def index():
   
    chart =  {"renderTo": 'container',"type": 'pie',"credits": {'enabled': 'false'}}
    title = {"text": 'Total plates for each specie',"align": 'center'}
    tooltip = {"headerFormat": '',"pointFormat": '<span style="color:{point.color}">\u25CF</span> <b> {point.name}</b><br/>' +
              'Strains : <b>{point.y}</b><br/>'+'Plates: <b>{point.z}</b><br/>'}
    series2 = scripts.strain_summary_json()
    colors_pie =  ['#244782','#0452d9','#82aefa']
    series = [{
        "minPointSize": 10,
        "innerSize": '20%',
        "zMin": 0,
        "name": 'species',
        "data" : series2,
      }]
    
    plate_series = scripts.plate_summary()
    chart_bar = {"renderTo":'container2',"type": 'bar',"credits": {'enabled': 'false'}}
    title_bar = {"text": 'Number of plates',
        "align": 'center'}
    xAxis =  {"categories": plate_series.index.tolist()}
    yAxis =  {"min": 0,"title": {"text": '',
            "align": 'high'},"labels": {"overflow": 'justify'}}
    colors_bar = ['#5993f7']
    tooltip_bar= {
        "valueSuffix": ' samples'}
    plotOptions_bar= {
        "bar": { "borderRadius": '0%',
            "dataLabels": {
                "enabled": 'true'
            },
        "column":{"colorByPoint": 'true'}
        }
    }
    legend_bar= {
        "layout": 'vertical',
        "align": 'right',
        "verticalAlign": 'top',
        "x": -40,
        "y": 80,
        "floating": 'true',
        "borderWidth": 1,
        "shadow":  'true'
    }
    credits_bar= {
        "enabled": 'false'
    }
    series_bar= [{"name": 'Upto 2023',"data": plate_series['num_plates'].tolist()}]

    return render_template('index.html', chartID='container', chart=chart, series=series,
                           title=title,tooltip=tooltip,colors_pie=colors_pie,chart_bar=chart_bar,title_bar = title_bar,
                            xAxis = xAxis,yAxis=yAxis,tooltip_bar=tooltip_bar,plotOptions_bar=plotOptions_bar,
                            legend_bar = legend_bar,credits_bar = credits_bar,series_bar = series_bar,colors_bar=colors_bar)

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


@app.route('/species', methods=['GET'])
def species():
    specie = request.args.get('specie')
    growth_max_resp,growth_max_resp_rate,growth_max_time,growth_max_auc,no_growth_max_resp,no_growth_max_resp_rate,no_growth_max_time,no_growth_max_auc,uncertain_growth_max_resp = scripts.get_control_well_distribution(specie)
    import random
    growth_max_resp=random.sample(growth_max_resp, 1000)
    no_growth_max_resp=random.sample(no_growth_max_resp, 1000)
    #uncertain_growth_max_resp = random.sample(uncertain_growth_max_resp,1000)
    #print(specie)
    #specie = 'ecoli'
    return render_template('species.html',specie=specie,gmax_resp=growth_max_resp,ngmax_resp=no_growth_max_resp,ug_max_resp=uncertain_growth_max_resp)


@app.route('/mainstraindata', methods=['GET'])
def mainstraindata():
    plateid = request.args.get('pltid')
    specie = request.args.get('strn')
    growth_calls,well_char,well_id,compound_dict = scripts.get_strain_data(plateid,specie)
    chart= {'type': 'heatmap','marginTop': 40,'marginBottom': 80,'plotBorderWidth': 1}
    title= {'text': ''}
    xAxis= {
        'categories': well_id,
        'labels':{'style':{'fontWeight':'bold','fontSize':'2em','fontFamily':'Monospace'}}
    }

    yAxis= {
        'categories': well_char,
        'title': 'null',
        'reversed': 'true',
        'labels':{'style':{'fontWeight':'bold','fontSize':'2em','fontFamily':'Monospace'}}
    }


    legend= {
        'enabled':'false',
        'align': 'right',
        'layout': 'vertical',
        'margin': 0,
        'verticalAlign': 'top',
        'y': 1,
        'symbolHeight': 280
    }

    series= [{
        'name': 'Growth(1)/No Growth(0)/Uncertain(0.5)',
        'borderWidth': 2.5,
        'borderColor':'#0a000f',
        'data': growth_calls,
        'dataLabels': {
            'enabled': 'false',
            'color': '#000000',
        }
    }]

    return render_template('mainstraindata.html',chartID='container', chart=chart, data=growth_calls,
                           title=title,legend = legend,xAxis = xAxis,yAxis=yAxis,compound_dict = compound_dict,pltid=plateid,strn=specie)


@app.route('/straindata', methods=['GET'])
def straindata():

    growth_calls,well_char,well_id,compound_dict = scripts.get_strain_data('ECP120')
    chart= {'type': 'heatmap','marginTop': 40,'marginBottom': 80,'plotBorderWidth': 1}
    title= {'text': ''}
    xAxis= {
        'categories': well_id,
        'labels':{'style':{'fontWeight':'bold','fontSize':'2em','fontFamily':'Monospace'}}
    }

    yAxis= {
        'categories': well_char,
        'title': 'null',
        'reversed': 'true',
        'labels':{'style':{'fontWeight':'bold','fontSize':'2em','fontFamily':'Monospace'}}
    }


    legend= {
        'enabled':'false',
        'align': 'right',
        'layout': 'vertical',
        'margin': 0,
        'verticalAlign': 'top',
        'y': 1,
        'symbolHeight': 280
    }

    series= [{
        'name': 'Growth(1)/No Growth(0)/Uncertain(0.5)',
        'borderWidth': 2.5,
        'borderColor':'#0a000f',
        'data': growth_calls,
        'dataLabels': {
            'enabled': 'false',
            'color': '#000000',
        }
    }]

    return render_template('straindata.html',chartID='container', chart=chart, data=growth_calls,
                           title=title,legend = legend,xAxis = xAxis,yAxis=yAxis,compound_dict = compound_dict)

@app.route('/strain_kinetics/json', methods=['GET'])
def strain_kinetics_json():
    #plateid = 'ECP120'
    #strain = request.args.get('strain')
    strain = request.args.get('spec')
    plateid = request.args.get('plate')
    out2 = scripts.get_kinetic_parameters(plateid,strain)
    
    return jsonify(data=out2)

@app.route('/get_growth_curves/json',methods=['POST'])
def get_growth_curves():
    well = request.form['well']
    plateid = request.form['plateid']
    specie = request.form['specie']
    chart_data = scripts.get_growth_curves(well,plateid,specie)
    return jsonify(chart_data) 


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
            "<a href="+url_for('mainstraindata',pltid=str(plateid),strn=request.args.get('strain'))+">"+str(plateid)+"</a>",
            #str(plateid),
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
