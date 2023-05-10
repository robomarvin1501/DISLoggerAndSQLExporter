import json

import pandas as pd
import os
import datetime

# log_file = open('log.csv', 'a')
ERROR_INT = -9999
GENERAL_STRUCTS = pd.read_csv("***REMOVED***/GeneralStructs.csv", index_col=[0])


def getListOfSubdirs(path):
    list_of_subdirs = list(os.walk(path))[0][1]
    all_dirs = []
    if len(list_of_subdirs) > 0:
        for dir in list_of_subdirs:
            full_path = os.path.join(path, dir)
            all_dirs.append(full_path)
            all_dirs = all_dirs + getListOfSubdirs(full_path)
    return all_dirs


def getAllFiles(path, exclude=()):
    all_files = []
    all_dirs_2_check = getListOfSubdirs(path)
    print(f'number of dirs to check: {len(all_dirs_2_check)}')

    for dir in all_dirs_2_check:
        files = list(os.walk(dir))[0][2]
        files = list(filter(lambda x: x not in exclude, files))
        all_files += [os.path.join(dir, i) for i in files]

    return all_files


def getErNum(str):  # EventReports always start with "[EventReport(er_num)]"
    def_er_str = '[EventReport('  # the string that starts every event report define
    num_start = len(def_er_str)
    num_end = str.strip().find(')')
    er_num = str.strip()[num_start:num_end]
    return int(er_num)


def getErName(str):  # EventReports def always start with "public class"
    def_er_str = 'public class '  # the string that starts every event report define
    name_start = len(def_er_str)
    name_end = str.strip().find(':')
    er_name = str.strip()[name_start:name_end]
    return er_name.strip()


def getVarDetails(str):
    details = str.replace(';', '').replace('static ', '').strip().split(' ')
    try:
        return details[1], details[2]
    except IndexError:
        print(f'{str} converted to {details} and is not in the right format')


def getErInfo(index, lines):
    opens = 0
    closes = 0
    info = list()
    while index < len(lines) and (opens == 0 or opens - closes != 0):
        line = lines[index]
        if line.find('//') != -1:
            line = line[:line.find('//')]
        if line.find('[EventReport(') != -1:
            if len(info) != 0:
                return info
            info.append(getErNum(line))
        elif line.find('public class') != -1 and line.find(':') != -1:
            info.append(getErName(line))
            print(f'Handling {getErName(line)} ({index})')
        elif line.find('public') != -1 and line.find(';') != -1:
            if line.find('enum') == -1:
                info.append(getVarDetails(line))
        elif line.find('{') != -1:
            opens += 1
        elif line.find('}') != -1:
            closes += 1
        index += 1
    return info


def get***REMOVED***ERs(unisim_er_file):
    print('Getting Unisim EventReports..')
    er_info = ['Name', 'Num', 'VarName', 'VarType']
    unisim_ers = pd.DataFrame(columns=er_info)
    with open(unisim_er_file, encoding='utf8') as txt:
        lines = txt.read().splitlines()
    for index in range(len(lines)):
        line = lines[index]
        print(line)
        if line.find('[EventReport(') != -1:
            info = getErInfo(index, lines)
            er_d = dict()
            er_d['Name'] = [info[1]]
            er_d['Num'] = [info[0]]
            for var in info[2:]:
                er_d['VarName'] = [var[1]]
                er_d['VarType'] = [var[0]]
                unisim_ers = unisim_ers.append(pd.DataFrame.from_dict(er_d))
    unisim_ers.reset_index(drop=True, inplace=True)
    # unisim_ers.to_excel('***REMOVED***ERs.xlsx')
    return unisim_ers


def getEnumOptions(index, lines):
    opens = 0
    closes = 0
    options_str = str()
    while index < len(lines) and (opens == 0 or opens - closes != 0):
        line = lines[index]
        if line.find('//') != -1:
            line = line[:line.find('//')]
        if line.find('{') != -1 and line.find('}') != -1:
            return line[line.find('{') + 1:line.find('}')].replace(' ', '').split(',')
        elif line.find('{') != -1:
            opens += 1
        elif line.find('}') != -1:
            closes += 1
        options_str += line.strip()
        index += 1
    options = options_str[options_str.find('{') + 1:options_str.find('}')].replace(' ', '').split(',')
    options = list(filter(None, options))
    return options


def getStructVars(index, lines):
    opens = 0
    closes = 0
    vars_str = str()
    while index < len(lines) and (opens == 0 or opens - closes != 0):
        line = lines[index]
        if line.find('//') != -1:
            line = line[:line.find('//')]
        # if line.find('{') != -1 and line.find('}') != -1:
        # 	return line[line.find('{')+1:line.find('}')].split(';')
        elif line.find('{') != -1:
            opens += 1
        elif line.find('}') != -1:
            closes += 1
        if opens - closes > 1 or line.find('(') != -1 or line.find(')') != -1 or line.find('*') != -1 or line.find(
                '#') != -1:
            index += 1
            continue
        vars_str += line.strip().replace('public ', '').replace('const ', '')
        index += 1
    vars = vars_str[vars_str.find('{') + 1:vars_str.find('}')].split(';')
    vars = list(filter(None, vars))
    return vars


def get***REMOVED***StructsAndEnums(unisim_files):
    enums_info = ['File', 'Name', 'Key', 'Value']
    enums = pd.DataFrame(columns=enums_info)

    structs_info = ['File', 'Name', 'VarName', 'VarType']
    structs = pd.DataFrame(columns=structs_info)

    print('Handling structs & enums...\n')
    for file in unisim_files:
        try:
            file_name = file[file.rindex('\\') + 1:]
        except ValueError:
            file_name = file
        try:
            with open(file, encoding='utf8') as txt:
                lines = txt.read().splitlines()
            for index in range(len(lines)):
                line = lines[index]
                if line.find('public') != -1 and not '//' in line[:line.find('public')]:
                    # handle structs:
                    if line.find(' struct ') != -1:
                        name = line.strip().split(' ')[2]
                        struct_vars = getStructVars(index, lines)
                        for var in struct_vars:
                            struct_d = dict()
                            struct_d['File'] = [file_name]
                            struct_d['Name'] = [name]
                            var_info = var.split(' ')
                            if var_info[0] == '':
                                continue
                            try:
                                struct_d['VarName'] = [var_info[1]]
                                struct_d['VarType'] = [var_info[0]]
                                structs = structs.append(pd.DataFrame.from_dict(struct_d))
                            except IndexError:
                                # print(f'ERROR WITH: {file}, {name}, {var}', file=log_file)
                                pass

                    # handle enums:
                    elif line.find(' enum ') != -1:
                        name = line.strip().split(' ')[2]
                        enum_options = getEnumOptions(index, lines)
                        for option in enum_options:
                            enum_d = dict()
                            enum_d['File'] = [file_name]
                            enum_d['Name'] = [name]
                            val = ERROR_INT
                            if option.find('=') != -1:
                                try:
                                    val = int(option[option.find('=') + 1:])
                                    option = option[:option.find('=')]
                                except ValueError:
                                    # print(f'ERROR WITH: {file}, {name}', file=log_file)
                                    pass
                            else:
                                val = enum_options.index(option)
                            enum_d['Key'] = [option]
                            enum_d['Value'] = [val]
                            enums = enums.append(pd.DataFrame.from_dict(enum_d))
            # log_file.write(f'{file}, SUCCESS\n')
        except UnicodeDecodeError:
            print(f'{file} has encoding issue')
            # log_file.write(f'{file}, FAILURE\n')

    enums.reset_index(drop=True, inplace=True)

    # add vector3 to structs:
    vector3 = {'File': ['MAIN'] * 3, 'Name': ['UnityEngine.Vector3'] * 3, 'VarName': ['X', 'Y', 'Z'],
               'VarType': ['float'] * 3}
    structs.append([pd.DataFrame.from_dict(vector3)])
    structs.reset_index(drop=True, inplace=True)

    # enums.to_excel('Enums.xlsx')
    # structs.to_excel('Structs.xlsx')
    return enums, structs


def json_to_file(json_data, file_name, path):
    with open(f"encoders/{path}/{file_name}.json", 'w', encoding="utf8") as f:
        json.dump(json_data, f, indent=4)


def create_dir():
    folder_dir = datetime.datetime.now().strftime('%Y-%m-%d_%H')
    output_folder = "encoders"
    path = os.path.join(os.getcwd(), output_folder, folder_dir)
    output_path = os.path.join(os.getcwd(), output_folder)

    if folder_dir not in os.listdir(output_path):
        os.mkdir(path)

    return folder_dir
