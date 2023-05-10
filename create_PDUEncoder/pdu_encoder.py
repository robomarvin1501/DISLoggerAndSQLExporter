import pandas as pd
import ***REMOVED***.Utils as u

CONFIG_FILE = "PduEncoder"


def get_event_report_info(er, ers_info_df):
    err_string = str()
    temp_df = pd.DataFrame()
    if type(er) == int:
        err_string = "ER num"
        temp_df = ers_info_df[ers_info_df["Num"] == er]
    elif type(er) == str:
        err_string = "ER name"
        temp_df = ers_info_df[ers_info_df["Name"] == er]
    if temp_df.empty:
        print(f"NO INFO ABOUT: {err_string} {er}")
        return
    return temp_df


def build_json(event_reports=(), event_reports_df=pd.DataFrame()):
    pdu_encoder = {}
    if len(event_reports) == 0:
        print("NO EVENT REPORTS PASSED")
        return
    for report in event_reports:
        report_df = get_event_report_info(report, event_reports_df)
        if report_df is None:
            continue

        name = report_df["Name"].iloc[0]
        num = report_df["Num"].iloc[0]

        event_report_json = {"event_name": name, "event_num": num, "FixedData": {}, "VariableData": {}}

        for i in report_df.index:
            var_name = report_df.loc[i]["XMLVarName"].strip()
            var_type = report_df.loc[i]["XMLVarType"].strip()

            if var_type in ("Int32", "Float64"):
                event_report_json["FixedData"][var_name] = var_type
            elif var_type == "ArrayByte":
                event_report_json["VariableData"][var_name] = var_type
            else:
                raise ValueError(f"{var_type} IS AN INVALID VAR TYPE")

        pdu_encoder[num] = event_report_json

    folder_dir = u.create_dir()
    u.json_to_file(pdu_encoder, CONFIG_FILE, folder_dir)
    return


def create_pdu_encoder(req_ers, ers_df=pd.DataFrame()):
    """
    LSE needs BLPduEncoder.xml config file to know which event reports to pull from network record
    and how to save them in prebuild SQL tables. This function takes list of event report names that you
    choose, dataframe with info about event report fields and creates this configuration file.
    """
    # buildConfigTree(req_ers)
    build_json(req_ers, ers_df)
