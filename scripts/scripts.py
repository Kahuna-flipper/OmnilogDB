import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
species = ['ecoli','pputida','saureus']

def strain_summary():

    strain_summary = pd.DataFrame(index=species)
    total_strains = []
    for specie in species:
        comp_strains = []
        temp_summary = pd.read_csv('./static/'+specie+'/metadata/project_summary.csv')
        strains = temp_summary['Strain']
        mods = temp_summary['Modification/Metadata']
        for st in range(0,len(strains)):
            comp_strains.append(strains[st]+mods[st])
        total_strains.append(len(list(set(comp_strains))))

    strain_summary['Num Strains'] = total_strains

    return strain_summary

