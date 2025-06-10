import pymysql
import pandas as pd
import os

def openExcelProcess(file_path):
    df = pd.read_excel(file_path, na_filter = False, sheet_name = "Procedimentos")
    return df

def openExcelActivity(file_path):
    df = pd.read_excel(file_path, na_filter = False, sheet_name = "Atividades")
    return df

def openExcelDocuments(file_path):
    df = pd.read_excel(file_path, na_filter = False, sheet_name = "Relação Documental")
    return df

def parseProcess(df, cursor):
    process_id = df["id"]
    process_name = df["Nome"]
    process_objective = df["Objetivo"]
    process_description = df["Descrição"]
    process_result = df["Qual o resultado expectável do procedimento?"]
    process_units = df["Unidades organizativas responsáveis pela execução do procedimento"]
    process_starting_units = df["Unidades organizativas iniciadoras do procedimento"]
    process_other_agents = df["Outros agentes envolvidos no procedimento"]
    process_subprocesses = df["Subprocessos"]
    process_internal_norms = df["Normativos internos"]
    process_external_norms = df["Normativos externos"]
    process_process_duration = df["Calendário/prazo de execução"]
    for i in range(len(process_id)):
        process_id_value = process_id[i]
        process_name_value = process_name[i]
        process_objective_value = process_objective[i]
        process_description_value = process_description[i]
        process_result_value = process_result[i]
        process_units_value = process_units[i].split(";")
        process_starting_units_value = process_starting_units[i].split(";")
        process_other_agents_value = process_other_agents[i].split(";")
        process_subprocesses_value = process_subprocesses[i].split(";")
        process_internal_norms_value = process_internal_norms[i]
        process_external_norms_value = process_external_norms[i]
        process_process_duration_value = process_process_duration[i]
        for unit in process_units_value:
            for starting_unit in process_starting_units_value:
                for other_agent in process_other_agents_value:
                    for subprocess in process_subprocesses_value:
                        pstmt = "INSERT INTO Process (ProcessID, ProcessName, ProcessObjective, ProcessDescription, ProcessResult, ProcessUnits, ProcessStartingUnits, OtherAgents, Subprocesses, InternalNorms, ExternalNorms, ProcessDuration) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(pstmt, (process_id_value, process_name_value, process_objective_value, process_description_value, process_result_value, unit.strip(), starting_unit.strip(), other_agent.strip(), subprocess.strip(), process_internal_norms_value, process_external_norms_value, process_process_duration_value))

def parseActivity(df, cursor):
    activity_id = df["id"]
    activity_process = df["Procedimento"]
    activity_name = df["Atividade"]
    activity_duration = df["Período/prazo/duração"]
    activity_description = df["Descrição"]
    activity_description_in_context = df["Descrição da responsabilidade no contexto do procedimento"]
    activity_system_used = df["Sistema informático utilizado"]
    activity_documents_used = df["Documentos utilizados"]
    for i in range(len(activity_id)):
        activity_id_value = activity_id[i]
        activity_process_value = activity_process[i]
        activity_name_value = activity_name[i]
        activity_duration_value = activity_duration[i]
        activity_description_value = activity_description[i]
        activity_description_in_context_value = activity_description_in_context[i]
        activity_system_used_value = activity_system_used[i]
        activity_documents_used_value = activity_documents_used[i].split(";")
        for document in activity_documents_used_value:
            pstmt = "INSERT INTO Activity (ActivityID, Process, ActivityName, ActivityDuration, ActivityDescription, ActivityDescriptionInContext, SystemUsed, DocumentsUsed) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(pstmt, (activity_id_value, activity_process_value, activity_name_value, activity_duration_value, activity_description_value, activity_description_in_context_value, activity_system_used_value, document.strip()))

def parseDocuments(df, cursor):
    documents_id = df["id"]
    documents_process = df["Procedimento"]
    document_name = df["Documento"]
    document_description = df["Referência/Descrição"]
    document_origin = df["Origem"]
    document_support = df["Suporte"]
    document_access_type = df["Acesso"]
    document_retention_time = df["Validade"]
    for i in range(len(documents_id)):
        documents_id_value = documents_id[i]
        documents_process_value = documents_process[i]
        document_name_value = document_name[i]
        document_description_value = document_description[i]
        document_origin_value = document_origin[i]
        document_support_value = document_support[i]
        document_access_type_value = document_access_type[i]
        document_retention_time_value = document_retention_time[i]
        pstmt = "INSERT INTO Documents (DocumentID, Process, DocumentName, DocumentDescription, DocumentOrigin, DocumentSupport, DocumentAccessType, DocumentRetentionTime) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(pstmt, (documents_id_value, documents_process_value, document_name_value, document_description_value, document_origin_value, document_support_value, document_access_type_value, document_retention_time_value))

def main():

    conn = pymysql.connect(
        user='BPMNuser',
        password='BPMNpass',   # Replace with your actual password
        host='localhost',           # Corrected host
        port=3306,                  # Corrected port
        database='BPMNManager'    # Replace with your actual database name
    )
    cursor = conn.cursor()

    path = '../DataSources/excel_departamentos/'
    files = os.listdir(path)

    # Print the files
    for file in files:
        if not os.path.isdir(os.path.join(path, file)) and file.endswith('.xlsx'):
            file_path = path + file
            process_df = openExcelProcess(file_path)
            activity_df = openExcelActivity(file_path)
            documents_df = openExcelDocuments(file_path)
            parseProcess(process_df, cursor)
            parseActivity(activity_df, cursor)
            parseDocuments(documents_df, cursor)

    conn.commit()
    cursor.close()

if __name__ == "__main__":
    main()