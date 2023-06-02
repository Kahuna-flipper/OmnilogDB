import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, url_for, jsonify
from flask import request

import smtplib
from email.message import EmailMessage

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

def get_kinetic_parameters(plateid,strain):
    growth_frame = pd.read_csv('static/'+strain+'/data/kinetic_summary.csv')
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
            # str(kegg),
            "<a href=https://www.genome.jp/entry/"+str(kegg)+">"+str(kegg)+"</a>",
            str(cas)])


    return out2
    #return jsonify(data=out2)


def get_growth_curves(well,plateid,specie):
    growth_curves = pd.read_csv('static/'+specie+'/data/plate_summary.csv')
    growth_curves = growth_curves.loc[growth_curves['PlateIDs']==plateid]
    main_growth_curves = growth_curves.loc[growth_curves['Well']==well]
    compound = main_growth_curves['Compound'].tolist()[0]
    plate = main_growth_curves['Plate'].tolist()[0]
    growth_data = []
    
    if('PM11' in plate or 'PM12' in plate):
        well_num = int(well[1:])
        well_num = well_num - ((well_num%4)-1)
        if(well_num<10):
            well_char = '0'+str(well_num)
        else:
            well_char = str(well_num)
        control_well = well[0]+well_char
        control_growth_curves = growth_curves.loc[growth_curves['Well']==control_well]
        control_compound = control_growth_curves['Compound'].tolist()[0]
        for i in range(0,main_growth_curves.shape[0]):
            temp_dict = {'name':compound+' R'+str(i),'data':main_growth_curves.iloc[i,8:].tolist()}
            growth_data.append(temp_dict)
        if(well!=control_well):
            for i in range(0,control_growth_curves.shape[0]):
                temp_dict = {'name':control_compound+' R'+str(i),'data':control_growth_curves.iloc[i,8:].tolist()}
                growth_data.append(temp_dict)

    elif('PM01' in plate or 'PM02' in plate or 'PM03' in plate or 'PM04' in plate or 'PM05' in plate or 'PM06' in plate or 'PM07' in plate or 'PM08' in plate):
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

    elif('PM09' in plate or 'PM10' in plate):
        for i in range(0,main_growth_curves.shape[0]):
            temp_dict = {'name':compound+' R'+str(i),'data':main_growth_curves.iloc[i,8:].tolist()}
            growth_data.append(temp_dict)

    time_scale = list(np.arange(0,48.25,0.25))

    chart_data = {'categories':time_scale,'data':growth_data}

    return chart_data




def get_control_well_distribution(specie):

    kinetic_data = pd.read_csv('static/'+specie+'/data/kinetic_summary.csv',index_col='PlateIDs')
    growth = kinetic_data.loc[kinetic_data['Growth(1)/No Growth(0)']==1]
    no_growth = kinetic_data.loc[kinetic_data['Growth(1)/No Growth(0)']==0]
    uncertain_growth = kinetic_data.loc[kinetic_data['Growth(1)/No Growth(0)']==0.5]

    growth_max_resp = growth['Max Resp'].tolist()
    growth_max_resp_rate = growth['Max Resp Rate'].tolist()
    growth_max_time = growth['Time till max resp rate'].tolist()
    growth_max_auc = growth['AUC'].tolist()


    no_growth_max_resp = no_growth['Max Resp'].tolist()
    no_growth_max_resp_rate = no_growth['Max Resp Rate'].tolist()
    no_growth_max_time = no_growth['Time till max resp rate'].tolist()
    no_growth_max_auc = no_growth['AUC'].tolist()


    uncertain_growth_max_resp = uncertain_growth['Max Resp'].tolist()

    return growth_max_resp,growth_max_resp_rate,growth_max_time,growth_max_auc,no_growth_max_resp,no_growth_max_resp_rate,no_growth_max_time,no_growth_max_auc,uncertain_growth_max_resp




def get_control_well_dist(specie):
    kinetic_data = pd.read_csv('static/'+specie+'/data/kinetic_summary.csv',index_col='PlateIDs')
    control_wells = kinetic_data.loc[kinetic_data['Well']=='A01']
    growth_wells = kinetic_data.loc[kinetic_data['Growth(1)/No Growth(0)']==1]
    control_data = []
    growth_data = []
    for well in range(0,control_wells.shape[0]):
        plate = control_wells.iloc[well,0]
        if('PM01' in plate or 'PM02' in plate or 'PM03' in plate or 'PM04' in plate or 'PM05' in plate or 'PM06' in plate or 'PM07' in plate or 'PM08' in plate):
            control_data.append(control_wells.iloc[well,5])
            growth_data.append(growth_wells.iloc[well,5])

    return control_data,growth_data



def send_email(name, email, message):
    msg = EmailMessage()
    msg.set_content(f'Name: {name}\nEmail: {email}\n\n{message}')
    msg['Subject'] = 'Contact Form Submission'
    msg['From'] = ''  # Replace with your own email address
    msg['To'] = ''  # Replace with your own email address

    # SMTP setup
    smtp_server = 'smtp.gmail.com'  # Replace with your SMTP server address
    smtp_port = 587  # Replace with your SMTP server port
    smtp_username = ''  # Replace with your SMTP server username
    smtp_password = ''  # Replace with your SMTP server password

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)


def process_entries(selected_entries):
    for entry in selected_entries:
        # Process each selected entry as needed
        print(f'Selected entry: {entry}')
        # Send email, perform database operations, etc.


def combine_specie_summaries():
    summary= pd.DataFrame()
    for specie in species:
        temp_dataframe = pd.DataFrame()
        strains = []
        strain_id = []
        mods = []
        sps = []
        temp_summary = pd.read_csv('static/'+specie+'/metadata/summary.csv',index_col='PlateIDs')
        for i in range(0,temp_summary.shape[0]):
            strains.append(temp_summary.iloc[i,1]+'___'+temp_summary.iloc[i,2])
        strains = list(set(strains))

        for strain in strains:
            strain_id.append(strain.split('___')[0])
            mods.append(strain.split('___')[1])
            sps.append(temp_summary['Specie'].tolist().pop(0))
        
        temp_dataframe['Strain ID'] = strain_id
        temp_dataframe['Modification'] = mods
        temp_dataframe['Specie'] = sps
        summary = pd.concat([summary,temp_dataframe])
    return summary.to_dict('records')



def get_all_compounds_in_all_wells():
    platedesc = pd.read_csv('static/plate_desc/platedesc.csv')
    compounds = []

    for i in range(0,platedesc.shape[0]):
        compounds.append(platedesc.iloc[i,2]+', '+platedesc.iloc[i,3])
    
    compounds = list(set(compounds))

    return compounds



def get_plate_well_from_compound(compound):
    platedesc = pd.read_csv('static/plate_desc/platedesc.csv')

    for i in range(platedesc.shape[0]):
        combined_comp = platedesc['Compound'][i]+', '+platedesc['Description'][i]
        if(compound==combined_comp):
            plate = platedesc['Plate'][i]
            well = platedesc['Well'][i]
        
    return plate,well


def get_plateid_from_strain(strain_list,plate):
    
    combined_summary = pd.DataFrame()
    plateids = []

    for specie in species:
        temp_summary = pd.read_csv('static/'+specie+'/metadata/summary.csv',index_col='PlateIDs')
        combined_summary = pd.concat([combined_summary,temp_summary])

    for i in range(0,len(strain_list),3):
        strain = combined_summary[combined_summary['Strain']==strain_list[i]]
        metadata = strain[strain['Modification/Metadata']==strain_list[i+1]]
        plates = metadata['Plate'].tolist()

        if(plate in plates):
            plateids.append((metadata[metadata['Plate']==plate]).index.tolist().pop(0))
        
        else:
            plateids.append('N.A')
    

    return plateids
    

def get_growth_calls_from_plateids(plateids,well,xlabels):
    combined_growth = pd.DataFrame()
    combined_signals = pd.DataFrame()
    growth_calls = []
    series = []

    for specie in species:
        temp_growth = pd.read_csv('static/'+specie+'/data/growth_summary.csv',index_col='PlateIDs')
        temp_signal = pd.read_csv('static/'+specie+'/data/plate_summary.csv',index_col='PlateIDs')
        combined_growth = pd.concat([combined_growth,temp_growth])
        combined_signals = pd.concat([combined_signals,temp_signal])
    
    i = 0
    for id in plateids:
        if(id=='N.A'):
            growth_calls.append([i,0,0.75])
        else:
            growth = combined_growth.loc[id]
            growth_calls.append([i,0,growth[growth['Well']==well]['Growth(1)/No Growth(0)/NA(0.5)'].tolist().pop()])
        i = i+1

    j = 0
    for id in plateids:
        if(id=='N.A'):
            j = j+1
            continue
        else:
            signals = combined_signals.loc[id]
            signals = signals[signals['Well']==well]
            for i in range(0,signals.shape[0]):
                if(i>=2):
                    break
                series.append({'name':xlabels[j]+' R'+str(i+1),'data':signals.iloc[i,7:].tolist()})

        j = j+1

    time = list(np.linspace(0,48,193))

    return growth_calls,series,time

    



def get_strain_names(strainlist):
    strain_names = []
    for i in range(0,len(strainlist),3):
        strain_names.append(strainlist[i]+'__'+strainlist[i+1]+'__'+strainlist[i+2])
    return strain_names
