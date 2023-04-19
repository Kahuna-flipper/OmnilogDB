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


    return True
