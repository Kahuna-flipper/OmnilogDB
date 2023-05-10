import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, url_for, jsonify
from flask import request

species = ['ecoli','pputida','saureus']

def strain_summary():

    strain_summary = pd.DataFrame(index=species)
    total_strains = []
    total_plates = []
    for specie in species:
        comp_strains = []
        #temp_summary = pd.read_csv(url_for('static',filename=specie+'/metadata/summary.csv'))
        temp_summary = pd.read_csv('static/'+specie+'/metadata/summary.csv')
        total_plates.append(temp_summary.shape[0])
        strains = temp_summary['Strain']
        mods = temp_summary['Modification/Metadata']
        for st in range(0,len(strains)):
            comp_strains.append(strains[st]+mods[st])
        total_strains.append(len(list(set(comp_strains))))

    strain_summary['Num Strains'] = total_strains
    strain_summary['Num Plates'] = total_plates

    return strain_summary


def strain_summary_json():

    total_strains = strain_summary()
    out2 = []

    for i in total_strains.index:
        num_specie = total_strains.loc[i,'Num Strains']
        num_plates = total_strains.loc[i,'Num Plates']
        specie = i
        temp_dict = {"name":specie,"y":num_specie,"z":num_plates}
        out2.append(temp_dict)

    return out2


def plate_summary():
    concat_summary = pd.DataFrame()
    for specie in species:
        temp_summary = pd.read_csv('static/'+specie+'/metadata/summary.csv')
        concat_summary = pd.concat([concat_summary,temp_summary])
    plates = concat_summary['Plate'].unique()

    total_plates = []

    for plate in plates:
        total_plates.append(concat_summary.loc[concat_summary['Plate']==plate].shape[0])

    total_plates_used = pd.DataFrame(index=plates)

    total_plates_used['num_plates'] = total_plates

    return total_plates_used


def get_strain_data(plateid,specie):
    well_char = ['A','B','C','D','E','F','G','H']
    well_num = ['01','02','03','04','05','06','07','08','09','10','11','12']
    growth_frame = pd.read_csv('static/'+specie+'/data/growth_summary.csv',index_col='PlateIDs')
    growth_frame = growth_frame.loc[plateid]
    growth_calls = np.array(growth_frame['Growth(1)/No Growth(0)/NA(0.5)'])
    growth_data = []
    growth_calls = growth_calls.reshape((8,12))

    compounds = growth_frame.iloc[:,3:5]
    compound_dict = {}

    for i in range (0,compounds.shape[0]):
        compound_dict[compounds.iloc[i,0]] = compounds.iloc[i,1]

    for i in range(0,12):
        for j in range(0,8):
            growth_data.append([i,j,growth_calls[j,i]])

    return growth_data,well_char,well_num,compound_dict

def get_kinetic_parameters(plateid):
    specie = 'ecoli'
    growth_frame = pd.read_csv('static/'+specie+'/data/kinetic_summary.csv')
    growth_frame = growth_frame.loc[growth_frame['PlateIDs']==plateid]

    out2 = []

    for i in growth_frame.index:
        plateid = growth_frame.loc[i,'PlateIDs']
        plate = growth_frame.loc[i,'Plate']
        well = growth_frame.loc[i,'Well']
        compound = growth_frame.loc[i,'Compound']
        max_resp = round(growth_frame.loc[i,'Max Resp'],1)
        max_resp_rate = round(growth_frame.loc[i,'Max Resp Rate'],1)
        time = growth_frame.loc[i,'Time till max resp rate']
        auc = round(growth_frame.loc[i,'AUC'],1)
        z = round(growth_frame.loc[i,'Z-score'],1)
        growth = growth_frame.loc[i,'Growth(1)/No Growth(0)']
        kegg = growth_frame.loc[i,'KEGG ID']
        cas = growth_frame.loc[i,'CAS ID']

        out2.append([
            str(plateid),
            str(plate),
            str(well),
            str(compound),
            str(max_resp),
            str(max_resp_rate),
            str(time),
            str(auc),
            str(z),
            str(growth),
            str(kegg),
            str(cas)])


    return out2
    #return jsonify(data=out2)


def get_growth_curves(well,plateid):
    specie = 'ecoli'
    growth_curves = pd.read_csv('static/'+specie+'/data/plate_summary.csv')
    growth_curves = growth_curves.loc[growth_curves['PlateIDs']==plateid]
    main_growth_curves = growth_curves.loc[growth_curves['Well']==well]
    compound = main_growth_curves['Compound'].tolist()[0]
    plate = main_growth_curves['Plate'].tolist()[0]
    growth_data = []
    
    if('PM11' in plate or 'PM12' in plate):
        control_well = well[0]+'01'
        control_growth_curves = growth_curves.loc[growth_curves['Well']==control_well]
        control_compound = control_growth_curves['Compound'].tolist()[0]
        for i in range(0,main_growth_curves.shape[0]):
            temp_dict = {'name':compound+' R'+str(i),'data':main_growth_curves.iloc[i,8:].tolist()}
            growth_data.append(temp_dict)
        if(well!=control_well):
            for i in range(0,control_growth_curves.shape[0]):
                temp_dict = {'name':control_compound+' R'+str(i),'data':control_growth_curves.iloc[i,8:].tolist()}
                growth_data.append(temp_dict)

    if('PM01' in plate or 'PM02' in plate or 'PM03' in plate or 'PM04' in plate or 'PM05' in plate or 'PM06' in plate or 'PM07' in plate or 'PM08' in plate):
        control_well = 'A01'
        control_growth_curves = growth_curves.loc[growth_curves['Well']==control_well]
        control_compound = control_growth_curves['Compound'].tolist()[0]
        for i in range(0,main_growth_curves.shape[0]):
            temp_dict = {'name':compound+' R'+str(i),'data':main_growth_curves.iloc[i,8:].tolist()}
            growth_data.append(temp_dict)
        if(well!='A01'):
            for i in range(0,control_growth_curves.shape[0]):
                temp_dict = {'name':control_compound+' R'+str(i),'data':control_growth_curves.iloc[i,8:].tolist()}
                growth_data.append(temp_dict)

    if('PM09' in plate or 'PM10' in plate):
        for i in range(0,main_growth_curves.shape[0]):
            temp_dict = {'name':compound+' R'+str(i),'data':main_growth_curves.iloc[i,8:].tolist()}
            growth_data.append(temp_dict)

    time_scale = list(np.arange(0,48.25,0.25))

    chart_data = {'categories':time_scale,'data':growth_data}

    return chart_data