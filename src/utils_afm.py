"""
AFM Data Processing Utility Functions

This module contains functions for processing and analyzing AFM (Atomic Force Microscopy) data.
Functions are organized into the following categories:

1. Loading and Saving
   - File I/O operations
   - Path handling
   - Data import/export

2. Data Processing
   - Data frame selection and manipulation
   - Edge cutting
   - Area extraction
   - Fitting and averaging

3. Visualization
   - Color selection
   - Range setting
   - Image saving
   - GIF creation
   - Histogram generation
   - Statistical plotting

4. Data Analysis
   - Statistical calculations
   - Line profile extraction
   - Peak detection
   - Gaussian fitting

5. Drift Analysis
   - Drift calculation
   - Offset determination
   - Drift list management
   - Maximum drift detection

6. Helper Functions
   - String parsing
   - Time extraction
   - Color mapping
   - Array conversion

7. Pipeline Functions
   - Topography processing pipeline
   - Current processing pipeline
   - Error processing pipeline
   - Data assembly

Each function is documented with its specific purpose and parameters.
"""

# Importing necessary libraries
import pandas as pd
import numpy as np
import sys
import os
import shutil #from skimage.feature import peak_local_max, find_peaks


path = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))



###############################################################################
#   Global Variables    
###############################################################################
# Statistics lists for storing measurement values
statistics_current = []
statistics_topo = []
statistics_error = []
statistics_current_gb = []
statistics_current_grain = []

# Data frame lists for storing processed data
dataframes_current = []
dataframes_topo = []
dataframes_error = []

# Line scan data lists
datalines_current = []
datalines_topo = []
datalines_distance = []

# Drift tracking variables
array_old = 0  # Previous array for drift calculation
array_old2 = 0  # Secondary previous array for drift calculation
offset_by_drift = (0, 0)  # Cumulative drift offset
offset_by_drift2 = (0, 0)  # Secondary drift offset


##################################################################################################
########################## Functions for Loading and Saving ######################################
##################################################################################################

def sortandlist(path):
    # Get list of files in the directory
    names = os.listdir(path)
    
    # Filter files by type
    files_topo = [k for k in names if "Topography" in k]
    files_amp = [k for k in names if "Amplitude" in k]
    files_phase = [k for k in names if "Phase" in k]  
    files_error = [k for k in names if "Error" in k]
    files_current = [k for k in names if "Current" in k]
    
    # Sort files by name, so the program goes through them chronologically
    files_topo = sorted(files_topo)
    files_amp = sorted(files_amp)
    files_phase = sorted(files_phase) 
    files_error = sorted(files_error)       
    files_current = sorted(files_current)
    
    # All files are listed here as an overview before the process starts
    print( "Folgende Current Dateien werden bearbeitet:" )
    print(files_current)
    print( "Folgende Topography Dateien werden bearbeitet:") 
    print(files_topo)
    print( "Folgende Amplituden Dateien werden bearbeitet:" )
    print(files_amp)
    print "Folgende Phasen Dateien werden bearbeitet:" 
    print(files_phase)
    print "Folgende Error Dateien werden bearbeitet:" 
    print(files_error)
    # Get Number of Elements in List for overall Histogram Plot 
    N = len(files_topo)
    print "Number of treated elements:"
    print(N)
    return N, files_topo, files_current, files_amp, files_phase, files_error

def make_folders(path):
    # Working path in which the pdfs will be saved 
    try:
        os.makedirs(path + "PDFs")        
    except OSError:
        print ("Folder exists already, will be deleted and replaced by new one")
        shutil.rmtree(path + "PDFs")
        os.makedirs(path + "PDFs")        
    else:
        print ("Successfully made new folder") 
    # Working path in which the jpgs will be saved 
    try:
        os.makedirs(path + "gifs")        
    except OSError:
        print ("Folder exists already, will be deleted and replaced by new one")
        shutil.rmtree(path + "gifs")
        os.makedirs(path + "gifs")        
    else:
        print ("Successfully made new folder") 
    # Working path in which the Histogramms will be saved 
    try:
        os.makedirs(path + "Histograms")        
    except OSError:
        print ("Folder exists already, will be deleted and replaced by new one")
        shutil.rmtree(path + "Histograms")
        os.makedirs(path + "Histograms")
    else:
        print ("Successfully made new folder") 
    # Working path in which the Linescans will be saved 
    try:
        os.makedirs(path + "Linescans")        
    except OSError:
        print ("Folder exists already, will be deleted and replaced by new one")
        shutil.rmtree(path + "Linescans")
        os.makedirs(path + "Linescans")
    else:
        print ("Successfully made new folder")         
    # Working path in which the Statistics csv plus Plots will be saved 
    try:
        os.makedirs(path + "Statistics")        
    except OSError:
        print ("Folder exists already, will be deleted and replaced by new one")
        shutil.rmtree(path + "Statistics")
        os.makedirs(path + "Statistics")
    else:
        print ("Successfully deleted and made new")     
        # Working path in which the fitted data will be stored  
    try:
        os.makedirs(path + "Fitted")        
    except OSError:
        print ("Folder exists already, will be deleted and replaced by new one")
        shutil.rmtree(path + "Fitted")
        os.makedirs(path + "Fitted")
    else:
        print ("Successfully deleted and made new")     
            # Working path in which the stable frame data will be stored  
    try:
        os.makedirs(path + "StableFrame")        
    except OSError:
        print ("Folder exists already, will be deleted and replaced by new one")
        shutil.rmtree(path + "StableFrame")
        os.makedirs(path + "StableFrame")
    else:
        print ("Successfully deleted and made new")      
                # Working path in which the jpgs will be stored  
    try:
        os.makedirs(path + "JPGs")        
    except OSError:
        print ("Folder exists already, will be deleted and replaced by new one")
        shutil.rmtree(path + "JPGs")
        os.makedirs(path + "JPGs")
    else:
        print ("Successfully deleted and made new")      
    path_pdfs = path + "PDFs"
    path_histo = path + "Histograms"    
    path_statistics = path + "Statistics"  
    path_gifs = path + "gifs"
    path_lines = path + "Linescans"
    path_fitted = path + "Fitted"
    path_stableframe = path + "StableFrame"
    path_jpgs = path + "JPGs"
    return path_pdfs, path_histo, path_statistics, path_gifs, path_jpgs, path_lines, path_fitted, path_stableframe

def get_time(list_of_filenames):
    """
    Extract timestamps from a list of filenames and return sorted list.
    
    Args:
        list_of_filenames (list): List of filenames containing timestamps
        
    Returns:
        list: List of extracted timestamps (first 9 chars only)
        
    Example:
        >>> get_time(['scan_001_20230401.dat', 'scan_002_20230402.dat'])
        ['20230401', '20230402']
    """
    # Sort filenames by timestamp
    sorted(list_of_filenames, key=extract_time)
    list_TIME = []
    
    for filename in list_of_filenames:
        ending = extract_time(filename)
        if ending:
            # Take first 9 chars of timestamp
            timestamp = ending[0:9]
            list_TIME.append(timestamp)
    
    return list_TIME

def extract_time(string):
    """
    Extract timestamp from a filename string that contains timestamp pattern.
    
    Args:
        string (str): Filename containing timestamp (e.g. 'scan_2.5V_20230401_001234.dat')
        
    Returns:
        str: Extracted timestamp string, or None if no timestamp found
        
    Example:
        >>> extract_time('scan_2.5V_20230401_001234.dat') 
        '20230401_001234'
    """
    for element in string.split("_"):
        # Look for elements starting with '00' and containing '.' 
        # This pattern matches typical timestamp formats
        if "00" in element and "." in element:
            return str(element)
    return None

def assemble(n, topo, error, current, amp, phase, time_list, path_new):
    """
    Assemble multiple scan types into combined .gwy files.
    
    Args:
        n (int): Number of scans
        topo (list): Topography scan files
        error (list): Error scan files  
        current (list): Current scan files
        amp (list): Amplitude scan files
        phase (list): Phase scan files
        time_list (list): Timestamps for each scan
        path_new (str): Output directory path
    """
    # Sort files by timestamp
    sorted(topo, key=extract_time)
    sorted(error, key=extract_time)
    sorted(current, key=extract_time)
    sorted(amp, key=extract_time)
    sorted(phase, key=extract_time)

    for i in range(len(topo)):
        print('Iteration run: i=')
        print(i)
        
        # Load topography data
        TOPO = topo[i]
        ids_topo, actcon_topo = load_data(path, TOPO)
        df_topo, name_topo = select_dataframe(actcon_topo, ids_topo[0])
        
        # Get output filename from timestamp
        name = time_list[i]
        print(name)
        
        # Add error data if available
        if len(error) == 0:
            print('The Error list is empty')
        else:
            ERROR = error[i]
            ids_error, actcon_error = load_data(path, ERROR)
            df_error, name_error = select_dataframe(actcon_error, ids_error[0])
            id_error = gwy.gwy_app_data_browser_add_data_field(df_error, actcon_topo, 1)
            actcon_topo['/' + str(id_error) +'/data/title'] = 'Error'
            remove(actcon_error)
       
        # Add current data if available
        if len(current) == 0:
            print('The current list is empty')
        else:
            CURRENT = current[i]
            ids_current, actcon_current = load_data(path, CURRENT)
            df_current, name_current = select_dataframe(actcon_current, ids_current[0])
            id_current = gwy.gwy_app_data_browser_add_data_field(df_current, actcon_topo, 2)
            actcon_topo['/' + str(id_current) +'/data/title'] = 'Current'
            remove(actcon_current)
                        
        # Add amplitude data if available
        if len(amp) == 0:
            print('The Amplitude list is empty')
        else:
            AMP = amp[i]
            ids_amp, actcon_amp = load_data(path, AMP)
            df_amp, name_amp = select_dataframe(actcon_amp, ids_amp[0])
            id_amp = gwy.gwy_app_data_browser_add_data_field(df_amp, actcon_topo, 3)
            actcon_topo['/' + str(id_amp) +'/data/title'] = 'Amplitude'
            remove(actcon_amp)    
            
        # Add phase data if available
        if len(phase) == 0:
            print('The Phase list is empty')
        else:
            PHASE = phase[i]
            ids_phase, actcon_phase = load_data(path, PHASE)
            df_phase, name_phase = select_dataframe(actcon_phase, ids_phase[0])
            id_phase = gwy.gwy_app_data_browser_add_data_field(df_phase, actcon_topo, 4)
            actcon_topo['/' + str(id_phase) +'/data/title'] = 'Phase'
            remove(actcon_phase) 
            
        # Save combined file
        actcon_topo = data_save(actcon_topo, name, path_newData, path)
        remove(actcon_topo)

    return

def load_data(path, name):
    print("Es wird gerade folgende Datei bearbeitet:")
    print(name)
    
    
    os.chdir(path)
    #Load data from path
    actcon = gwy.gwy_file_load(name, gwy.RUN_NONINTERACTIVE)
    #Load container into browser
    gwy.gwy_app_data_browser_add(actcon)
    #Ids is identifikation code or key of the active container 
    ids = gwy.gwy_app_data_browser_get_data_ids(actcon)
    print "With the following ids:"
    print ids
    return ids, actcon


def select_dataframe(actcon, parameter_name, key):
    #Select df with key id 0 since the tiff only has one 
    df = actcon[gwy.gwy_app_get_data_key_for_id(key)] 
    df_name = actcon["/" + str(key) +"/data/title"]
    print "The name of the datafield as represented in the gwy container:"
    print df_name
    title = df_name + " " + str(parameter_name) + " V"
    actcon["/" + str(key) +"/data/title"] = title
    #print actcon["/"key"/data/title"]
    #Select datafield so that the fit functions (gwy_process_func_run) are not confused
    gwy.gwy_app_data_browser_select_data_field(actcon, key)
    return df