import pandas as pd

import ***REMOVED***.Utils as u


def parse***REMOVED***ERs():
    '''
    All ***REMOVED*** event reports are stored in EventReports.cs file in ***REMOVED*** folder.
    This function parses this file, converts complex event reports field types (like EntityId) to basic ones that LSE "understands" (like int32 or ArrayByte),
    saves info about each event report inside of a dataframe (unisim_ers) and then returns it.
    '''
    
    # u.log_file.write(dt.today().strftime('DD/MM/YYYY'))

    # Translate event reports file to dataframe, including complex data types
    unisim_er_file = r'C:\Users\gidonr\Documents\***REMOVED***\Assets\NetSim\EventReports.cs'
    # if not os.path.exists(unisim_er_file):
    #     print(f'COULD NOT FIND {unisim_er_file}!', file=u.log_file)
    unisim_ers = u.get***REMOVED***ERs(unisim_er_file)

    # Gets all files (their pathes) in Assets folder (except PitchDISTest, for some reason)
    unisim_path = r'C:\Users\gidonr\Documents\***REMOVED***\Assets'
    unisim_exclude_files = ('PitchDISTest.cs')
    unisim_files = list(filter(lambda x: (x[-3:] == '.cs'), u.getAllFiles(unisim_path, unisim_exclude_files)))

    # Loading structs and enums in order to translate these data types into basic ones
    unisim_enums, unisim_structs = u.get***REMOVED***StructsAndEnums(unisim_files)

    # Mark if struct inner variable is struct or enum
    unisim_structs['IsStruct'] = unisim_structs['VarType'].apply(lambda x: 1 if x in unisim_structs['Name'].unique() else 0)
    unisim_structs['IsEnum'] = unisim_structs['VarType'].apply(lambda x: 1 if x in unisim_enums['Name'].unique() else 0)

    # Append "explanation" of structs-type inner variables
    unisim_structs = unisim_structs.merge(unisim_structs[['Name', 'VarName', 'VarType']], how='left', left_on='VarType', right_on='Name')


    def structXMLVarName(row):
        if row['IsStruct'] == 1:
            name = row['Name_x']
            if not pd.isna(row['VarName_x']):
                name += row['VarName_x']
            if not pd.isna(row['VarName_y']):
                name += row['VarName_y']
            return name
        else:
            return row['VarName_x']


    def structXMLVarType(row):
        if not pd.isna(row['VarType_y']):
            return row['VarType_y']
        elif row['IsEnum'] == 1:
            return 'int'
        elif not pd.isna(row['VarType_x']):
            return row['VarType_x']

    # Preparing xml variable name, by default it is equal to variable name, but if it is struct it concatenates variable name and
    # inner variable name, for some reason. My guess is - to make uniquely named columns.
    unisim_structs['XMLVarName'] = unisim_structs.apply(lambda row: structXMLVarName(row), axis=1)

    # Preparing xml variable type. Takes variable type, if variable is struct - takes inner variable type.
    unisim_structs['XMLVarType'] = unisim_structs.apply(lambda row: structXMLVarType(row), axis=1)

    # Cut everything before . in VarTypes. Example: "UnityEngine.Vector3" -> "Vector3"
    unisim_ers['VarType'] = unisim_ers.apply(lambda row: row['VarType'] if row['VarType'].find('.') == -1 else row['VarType'][row['VarType'].rfind('.') + 1:], axis=1)

    # Add the XML info about every struct variable in unisim_ers 
    unisim_structs_cols = ['Name_x', 'XMLVarName', 'XMLVarType']
    unisim_ers = unisim_ers.merge(unisim_structs[unisim_structs_cols], how='left', left_on='VarType', right_on='Name_x')

    # If XMLVarType is empty for some reason, put VarType there (I think it is intended to work with structs
    # that weren't found in Assets folder, but I'm not 100% sure here)
    unisim_ers['XMLVarType'] = unisim_ers.apply(lambda row: row['XMLVarType'] if not pd.isna(row['XMLVarType']) else row['VarType'], axis=1)

    # Cut everything before . in XMLVarTypes. Example: "UnityEngine.Vector3" -> "Vector3"
    unisim_ers['XMLVarType'] = unisim_ers.apply(lambda row: row['XMLVarType'] if row['XMLVarType'].find('.') == -1 else row['XMLVarType'][row['XMLVarType'].rfind('.') + 1:], axis=1)

    # Add the XML info about every enum variable in unisim_ers 
    unisim_ers = unisim_ers.merge(unisim_enums[['Name']].drop_duplicates(), how='left', left_on='XMLVarType', right_on='Name', suffixes=('', '_y'))

    # If XMLVarType is not empty, put int. If it is - put enum name (I think it is intended to work with enums
    # that weren't found in Assets folder, but I'm not 100% sure here)
    unisim_ers['XMLVarType'] = unisim_ers.apply(lambda row: 'int' if not pd.isna(row['Name_y']) else row['XMLVarType'], axis=1)

    # If XMLVarType is empty - put VarName instead. Againg, it looks like it is for enums that were not found.
    unisim_ers['XMLVarName'] = unisim_ers.apply(lambda row: row['XMLVarName'] if not pd.isna(row['XMLVarName']) else row['VarName'], axis=1)

    # Add info about manualy defined structs
    unisim_ers = unisim_ers.merge(u.GENERAL_STRUCTS, left_on='VarType', right_on='Name', how='left', suffixes=('', '_gs'))

    # For manually defined structs XMLVarName will be equal VarName regular + manual VarName. Maybe for making them unique
    def debug_f(row):
        try:
            return row['VarName'] + row['VarName_gs'] if not pd.isna(row['Name_gs']) else row['XMLVarName']
        except TypeError:
            print(row)
            exit

    unisim_ers['XMLVarName'] = unisim_ers.apply(debug_f, axis=1)
    # unisim_ers['XMLVarName'] = unisim_ers.apply(lambda row: row['VarName'] + row['VarName_gs'] if not pd.isna(row['Name_gs']) else row['XMLVarName'], axis=1)

    # If there is manually defined VarType for something, override XMLVarType
    unisim_ers['XMLVarType'] = unisim_ers.apply(lambda row: row['VarType_gs'] if not pd.isna(row['VarType_gs']) else row['XMLVarType'], axis=1)

    to_xml_type = {
        'float': "Float64",
        'int': "Int32",
        'ushort': "Int32",
        'bool': "Int32",
        'string': "ArrayByte",
        'double': "Float64",
        'uint': "Int32"
    }

    checkit = list(filter(lambda x: x not in to_xml_type, unisim_ers['XMLVarType'].unique()))

    # If XMLVarType can be tranlated - do it
    unisim_ers['XMLVarType'] = unisim_ers['XMLVarType'].apply(lambda x: to_xml_type[x] if x in to_xml_type else x)

    # Choose relevant columns
    cols_for_lse = ['Name', 'Num', 'XMLVarName', 'XMLVarType']

    # Save as ***REMOVED***ERs.xlsx
    # unisim_ers[cols_for_lse].to_excel('***REMOVED***ERs.xlsx')

    # # Write to log all types that weren't "translatable", in case user wants to know this
    # unisim_ers[cols_for_lse][unisim_ers['XMLVarType'].isin(checkit)].to_excel('ExcludedFields.xlsx')

    print('FINISHED CREATING ***REMOVED***ERs.xlsx')

    return unisim_ers[cols_for_lse]