import pandas as pd

def clean_types(d):
    new_d = {}
    for k, v in d.items():
        if isinstance(v, float) and v.is_integer():
            new_d[k] = int(v)
        else:
            new_d[k] = v
    return new_d

def convert_data_point_to_text(data_point):
    out = []
    for i,j in data_point.items():
        row = f'{i} : {j}'
        out.append(row)
    return '\n'.join(out)

def data_cleaning(df):
    new_df = df.copy().ffill()
    rows = []
    for _, temp in new_df.groupby('Variable'):
        temp = temp.astype(str)
        to_append = {col: "|".join(temp[col].unique()) for col in temp.columns}
        rows.append(to_append)
    cleaned_df = pd.DataFrame(rows)
    return cleaned_df

def convert_val_to_dict(val):
    if val =='Not Applicable':
        return {}
    elif '|' in val:
        pairs = [i.split('=') for i in val.split('|') if '=' in i]
        res = {k.strip(): w.strip() for k,w in pairs}
        return res
    else:
        return {}

def convert_dict_keys_to_int(input_dict):
    return {int(i): j for i,j in  input_dict.items()}

class PatientDataStore:
    def __init__(self, data_schema_file = None, patient_data_file = None):
        self.data_schema_file = data_schema_file or '/mnt/f/chat_ui/data/data_schema.xlsx'
        self.patient_data_file = patient_data_file or '/mnt/f/chat_ui/data/health dataset.xlsx'

        self.nominal_columns_with_mappings, self.variable_to_label_mapping = self.process_data_schema()
        self.patient_data = self.get_patient_data()

    def process_data_schema(self):
        df = pd.read_excel(self.data_schema_file)
        clean_df =  data_cleaning(df)
        clean_df['Value Labels Cleaned'] = clean_df['Value Labels'].apply(convert_val_to_dict)
        clean_df['Variable Label'] = clean_df['Variable Label'].apply(lambda x: x.replace('|', ' '))
        clean_df['Position'] = clean_df['Position'].apply(lambda x: x.split('.')[0]).astype(int)
        clean_df = clean_df.sort_values(by='Position', ascending=True)

        nominal_columns_with_mappings = {col: mapping \
                for col, mapping in clean_df[['Variable','Value Labels Cleaned']].itertuples(index=False) if mapping }
        
        nominal_columns_with_mappings = {i: convert_dict_keys_to_int(j) for i,j in nominal_columns_with_mappings.items()}
        
        for col, label_dict in nominal_columns_with_mappings.items():
            label_dict[-1] = 'Unknown' 

        variable_to_label_mapping = {variable: label \
                for variable, label in clean_df[['Variable','Variable Label']].itertuples(index=False)}
        return nominal_columns_with_mappings, variable_to_label_mapping
        
    def get_patient_data(self):
        patient_data = pd.read_excel(self.patient_data_file)

        patient_data['Pregnancy'] = patient_data['Pregnancy'].fillna(0)
        patient_data['alcohol_consumption_per_day'] = patient_data['alcohol_consumption_per_day'].fillna(0)
        patient_data['Genetic_Pedigree_Coefficient'] = patient_data['Genetic_Pedigree_Coefficient'].fillna(0)

        for col, label_mapping in self.nominal_columns_with_mappings.items():
            patient_data[col] = patient_data[col].fillna(-1)
            patient_data[col] = patient_data[col].map(label_mapping)

        return patient_data
    
    def get_patient_record(self, row_num=0):
        data_point = self.patient_data.iloc[row_num].to_dict()
        return data_point
    
    def convert_data_point_to_text(self, data_point):
        out = []
        for i,j in data_point.items():
            row = f'{i} : {j}'
            out.append(row)
        return '\n'.join(out)

    def get_prompt_for_single_patient(self, data_points, patient_record):
        system_prompt = f"""
        System:\n\nYou are a healthcare expert. You will be provided data points from patient report.
        You have to analyze the data points and write a 100 to 500 word report on patient health.
        Here are the fields expected in patient report:
        ===
        {data_points}
        ===
        """
        user_prompt = f'USER:\n\n{self.convert_data_point_to_text(patient_record)}'
        final_prompt = '\n'.join([system_prompt, user_prompt])
        return final_prompt