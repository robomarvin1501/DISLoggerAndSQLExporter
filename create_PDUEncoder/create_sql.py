import ***REMOVED***.Utils as u

import json

from ***REMOVED***.Tools import sqlConn


def create_event_report_tables(db_name: str, encoder_config_path=""):
    """
    Before LSE saves all event reports that Logger recorded, it needs the SQL tables. This function
    takes database name, reads the PduEncoder.json, created by the create_pdu_encoder function, and creates those tables
    in the given database. If table is empty it will delete it and create a new one.
    :param db_name: str
    :param encoder_config_path: str
    :return:
    """
    # Moved out of the default values because it kept creating the folder, even when not creating a new DB
    if encoder_config_path == "":
        encoder_config_path = f"./encoders/{u.create_dir()}/PDUEncoder.json"

    create_base_tables(db_name)

    sql_types = {
        "Float64": "[float]",
        "Int32": "[int]",
        "ArrayByte": "[nvarchar](500)"
    }

    field_template = "[{field_name}] {field_type} NULL,"

    default_fields = [
        "[SenderIdSite] [int] NULL,",
        "[SenderIdHost] [int] NULL,",
        "[SenderIdNum] [int] NULL,",
        "[ReceiverIdSite] [int] NULL,",
        "[ReceiverIdHost] [int] NULL,",
        "[ReceiverIdNum] [int] NULL,",
        "[WorldTime] [datetime] NULL,",
        "[PacketTime] [float] NULL,",
        "[LoggerFile] [nvarchar](500) NULL,",
        "[ExportTime] [datetime] NOT NULL,",
        "[ExerciseId] [int] NULL,",
        "[ExporterMarkingText] [nvarchar](50) NULL,",
        "[PlayStop] [nvarchar](4) NULL"
    ]

    drop_if_empty_template = """
    IF EXISTS (SELECT * FROM sys.objects WHERE name = '{event_report_name}' AND type = 'U')
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM [dis].{event_report_name})
        BEGIN
        DROP TABLE [dis].{event_report_name}
        END
    END
    """

    if_exists_template = """
    {drop_if_empty_part}
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = '{event_report_name}' AND type = 'U')
    BEGIN
    {create_table_part}
    END
    """

    default_template = """
    CREATE TABLE [dis].[{current_event_report_name}](
    {fields})
    """

    # =================================================================================================================
    conn = sqlConn(db_name)

    event_reports = {}

    with open(encoder_config_path, 'r', encoding="utf8") as f:
        event_reports_unprocessed = json.load(f)

    for report in event_reports_unprocessed:
        event_reports[event_reports_unprocessed[report]["event_name"]] \
            = event_reports_unprocessed[report]["FixedData"] | event_reports_unprocessed[report]["VariableData"]

    # Create table queries
    # Container to save create table queries
    create_table_queries = {}
    drop_if_empty_parts = {}

    for report in event_reports:
        # Container to save each field query part
        event_report_specific_fields = []

        for field_name in event_reports[report]:
            current_query = field_template.format(
                field_name=field_name,
                field_type=sql_types[event_reports[report][field_name]]
            )
            event_report_specific_fields.append(current_query)

        # Add event report specific fields to default ones
        fields = event_report_specific_fields + default_fields

        # Add tabs and newlines to make the fields look nicer in the query
        fields = ['\t' + field + '\n' for field in fields]

        # Make create table part of the query
        result_query = default_template.format(
            current_event_report_name=report,
            fields=''.join(fields)
        )

        # Save 'Drop if empty part'
        drop_if_empty_part = drop_if_empty_template.format(event_report_name=report)
        drop_if_empty_parts[report] = drop_if_empty_part

        create_table_queries[report] = result_query

    full_queries = []

    for report in create_table_queries:
        # Add part that ensures they will be executed only if table does not exist
        query = if_exists_template.format(
            drop_if_empty_part=drop_if_empty_parts[report],
            event_report_name=report,
            create_table_part=create_table_queries[report]
        )

        conn.execute(query)
        conn.execute("COMMIT")

        # Save for possible future debugging
        full_queries.append(query)

    # Save the new query in case it needs to be checked
    tables_query = '\n'.join(full_queries)

    # Make sure that we won't run those queries in some other database in case we'll use this query
    final_query = f'USE [{db_name}]\nGO\n' + tables_query

    # Save full query

    with open(f'./encoders/{u.create_dir()}/create_event_reports_tables.sql', 'w', encoding='utf8') as f:
        f.write(final_query)


def create_base_tables(db_name: str):
    sql_conn = sqlConn(db_name)

    entity_state_ints = """

                IF EXISTS (SELECT * FROM sys.objects WHERE name = 'EntityStateInts' AND type = 'U')
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM [dis].EntityStateInts)
                    BEGIN
                    DROP TABLE [dis].EntityStateInts
                    END
                END
                    
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'EntityStateInts' AND type = 'U')
                BEGIN
                
                CREATE TABLE [dis].[EntityStateInts](
                    [SenderIdSite] [int] NULL,
                    [SenderIdHost] [int] NULL,
                    [SenderIdNum] [int] NULL,
                    [IntType] [nvarchar](50) NULL,
                    [IntValue] [int] NULL,
                    [WorldTime] [datetime] NULL,
                    [PacketTime] [real] NULL,
                    [LoggerFile] [nvarchar](400) NULL,
                    [ExportTime] [datetime] NOT NULL,
                    [ExerciseId] [int] NULL,
                    [ExporterMarkingText] [nvarchar](50) NULL,
                    [PlayStop] [nvarchar](4) NULL

                ) ON [PRIMARY]
                
                END
                
    """
    entity_state_locs = """

        IF EXISTS (SELECT * FROM sys.objects WHERE name = 'EntityStateLocations' AND type = 'U')
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM [dis].EntityStateLocations)
            BEGIN
            DROP TABLE [dis].EntityStateLocations
            END
        END
            
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'EntityStateLocations' AND type = 'U')
        BEGIN
        
        CREATE TABLE [dis].[EntityStateLocations](
            [SenderIdSite] [int] NULL,
            [SenderIdHost] [int] NULL,
            [SenderIdNum] [int] NULL,
            [GeoLocationX] [float] NULL,
            [GeoLocationY] [float] NULL,
            [GeoLocationZ] [float] NULL,
            [GeoVelocityX] [real] NULL,
            [GeoVelocityY] [real] NULL,
            [GeoVelocityZ] [real] NULL,
            [Psi] [real] NULL,
            [Theta] [real] NULL,
            [Phi] [real] NULL,
            [WorldTime] [datetime] NULL,
            [PacketTime] [real] NULL,
            [LoggerFile] [nvarchar](200) NULL,
            [ExportTime] [datetime] NOT NULL,
            [ExerciseId] [int] NULL,
            [ExporterMarkingText] [nvarchar](50) NULL,
            [PlayStop] [nvarchar](4) NULL
        ) ON [PRIMARY]
        
        END

    """
    entity_state_texts = """        
        IF EXISTS (SELECT * FROM sys.objects WHERE name = 'EntityStateTexts' AND type = 'U')
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM [dis].EntityStateTexts)
            BEGIN
            DROP TABLE [dis].EntityStateTexts
            END
        END
            
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'EntityStateTexts' AND type = 'U')
        BEGIN
        
        
        CREATE TABLE [dis].[EntityStateTexts](
            [SenderIdSite] [int] NULL,
            [SenderIdHost] [int] NULL,
            [SenderIdNum] [int] NULL,
            [TextType] [nvarchar](50) NULL,
            [TextValue] [nvarchar](50) NULL,
            [WorldTime] [datetime] NULL,
            [PacketTime] [real] NULL,
            [LoggerFile] [nvarchar](200) NULL,
            [ExportTime] [datetime] NOT NULL,
            [ExerciseId] [int] NULL,
            [ExporterMarkingText] [nvarchar](50) NULL,
            [PlayStop] [nvarchar](4) NULL
        ) ON [PRIMARY]
        
        END
        
    """

    fire_pdu = """

        
        IF EXISTS (SELECT * FROM sys.objects WHERE name = 'FirePdu' AND type = 'U')
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM [dis].FirePdu)
            BEGIN
            DROP TABLE [dis].FirePdu
            END
        END
            
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'FirePdu' AND type = 'U')
        BEGIN
        
        
        CREATE TABLE [dis].[FirePdu](
            [EventIdSite] [int] NULL,
            [EventIdHost] [int] NULL,
            [EventIdNum] [int] NULL,
            [AttackerIdSite] [int] NULL,
            [AttackerIdHost] [int] NULL,
            [AttackerIdNum] [int] NULL,
            [TargetIdSite] [int] NULL,
            [TargetIdHost] [int] NULL,
            [TargetIdNum] [int] NULL,
            [MunitionIdSite] [int] NULL,
            [MunitionIdHost] [int] NULL,
            [MunitionIdNum] [int] NULL,
            [GeoLocationX] [float] NULL,
            [GeoLocationY] [float] NULL,
            [GeoLocationZ] [float] NULL,
            [GeoVelocityX] [real] NULL,
            [GeoVelocityY] [real] NULL,
            [GeoVelocityZ] [real] NULL,
            [MunitionType] [nvarchar](50) NULL,
            [FuseType] [int] NULL,
            [Quantity] [int] NULL,
            [Range] [real] NULL,
            [WarheadType] [int] NULL,
            [WorldTime] [datetime] NULL,
            [PacketTime] [real] NULL,
            [LoggerFile] [nvarchar](200) NULL,
            [ExportTime] [datetime] NOT NULL,
            [ExerciseId] [int] NULL,
            [ExporterMarkingText] [nvarchar](50) NULL,
            [PlayStop] [nvarchar](4) NULL
        ) ON [PRIMARY]
        
        END
        
    """
    detonation_pdu = """                
        IF EXISTS (SELECT * FROM sys.objects WHERE name = 'DetonationPdu' AND type = 'U')
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM [dis].DetonationPdu)
            BEGIN
            DROP TABLE [dis].DetonationPdu
            END
        END
            
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'DetonationPdu' AND type = 'U')
        BEGIN
        
        
        CREATE TABLE [dis].[DetonationPdu](
            [EventIdSite] [int] NULL,
            [EventIdHost] [int] NULL,
            [EventIdNum] [int] NULL,
            [AttackerIdSite] [int] NULL,
            [AttackerIdHost] [int] NULL,
            [AttackerIdNum] [int] NULL,
            [TargetIdSite] [int] NULL,
            [TargetIdHost] [int] NULL,
            [TargetIdNum] [int] NULL,
            [MunitionIdSite] [int] NULL,
            [MunitionIdHost] [int] NULL,
            [MunitionIdNum] [int] NULL,
            [GeoLocationX] [float] NULL,
            [GeoLocationY] [float] NULL,
            [GeoLocationZ] [float] NULL,
            [GeoVelocityX] [real] NULL,
            [GeoVelocityY] [real] NULL,
            [GeoVelocityZ] [real] NULL,
            [MunitionType] [nvarchar](50) NULL,
            [FuseType] [int] NULL,
            [Quantity] [int] NULL,
            [WarheadType] [int] NULL,
            [WorldTime] [datetime] NULL,
            [PacketTime] [real] NULL,
            [LoggerFile] [nvarchar](200) NULL,
            [ExportTime] [datetime] NOT NULL,
            [ExerciseId] [int] NULL,
            [ExporterMarkingText] [nvarchar](50) NULL,
            [PlayStop] [nvarchar](4) NULL
        ) ON [PRIMARY]
        
        END
        
    """
    transmitter_pdu = """
            
        IF EXISTS (SELECT * FROM sys.objects WHERE name = 'TransmitterPDU' AND type = 'U')
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM [dis].TransmitterPDU)
            BEGIN
            DROP TABLE [dis].TransmitterPDU
            END
        END
            
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'TransmitterPDU' AND type = 'U')
        BEGIN
        
        CREATE TABLE [dis].[TransmitterPDU](
            [SenderIdSite] [int] NULL,
            [SenderIdHost] [int] NULL,
            [SenderIdNum] [int] NULL,
            [RadioID] [int] NULL,
            [RadioType] [nvarchar](50) NULL,
            [TransmitState] [int] NULL,
            [InputSource] [int] NULL,
            [AntennaLocationX] [float] NULL,
            [AntennaLocationY] [float] NULL,
            [AntennaLocationZ] [float] NULL,
            [RelativeAntennaLocationX] [float] NULL,
            [RelativeAntennaLocationY] [float] NULL,
            [RelativeAntennaLocationZ] [float] NULL,
            [AntennaPatternType] [int] NULL,
            [Frequency] [int] NULL,
            [TransmitFrequencyBandwidth] [real] NULL,
            [Power] [real] NULL,
            [WorldTime] [datetime] NULL,
            [PacketTime] [real] NULL,
            [LoggerFile] [nvarchar](200) NULL,
            [ExportTime] [datetime] NOT NULL,
            [ExerciseId] [int] NULL,
            [ExporterMarkingText] [nvarchar](50) NULL,
            [PlayStop] [nvarchar](4) NULL
        ) ON [PRIMARY]
        
        END        
    """

    base_tables = [entity_state_ints, entity_state_locs, entity_state_texts, fire_pdu, detonation_pdu, transmitter_pdu]

    for table in base_tables:
        sql_conn.execute(table)
        sql_conn.execute("COMMIT")


def ***REMOVED***(db_name: str, encoder_config_path=""):
    # Moved out of the default values because it kept creating the folder, even when not creating a new DB
    if encoder_config_path == "":
        encoder_config_path = f"./encoders/{u.create_dir()}/PDUEncoder.json"
    create_base_tables(db_name)
    create_event_report_tables(db_name, encoder_config_path)
