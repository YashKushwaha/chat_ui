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

class MetaDataManager:
    def __init__(self, metadata_file = None):
        self.metadata_file = metadata_file or '/mnt/f/chat_ui/data/data_schema.xlsx'
        self.metadata_df = self.get_metadata()

    def get_metadata(self):
        metadata_df = pd.read_excel(self.metadata_file)
        metadata_df = data_cleaning(metadata_df)
        return metadata_df 

    def get_column_descriptions(self, as_text=False):
        iterator = self.metadata_df[['Variable', 'Variable Label']].itertuples(index=False)
        res =  {col:desc for col, desc in iterator}
        if as_text:
            return self.dict_to_text(res)
        else:
            return res
        
    def dict_to_text(self, dict_to_convert):
        rows = []
        for i,j in dict_to_convert.items(): 
            rows.append(f'{i} : {j}')
        return '\n'.join(rows)

class PatientDataStore:
    def __init__(self, data_schema_file = None, patient_data_file = None):
        self.data_schema_file = data_schema_file or '/mnt/f/chat_ui/data/health_schema.xlsx'
        self.patient_data_file = patient_data_file or '/mnt/f/chat_ui/data/health_dataset.xlsx'

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
    
    def get_patient_record_old(self, row_num=0):
        data_point = self.patient_data.iloc[row_num].to_dict()
        return data_point
    
    def get_patient_record_old(self, patient_num= 1, row_num=0):
        if isinstance(patient_num, str):
            patient_num = int(patient_num)
        try:
            patient_num_in_db = patient_num in self.patient_data['Patient_Number'].unique()
            if patient_num_in_db:
                return self.patient_data[self.patient_data['Patient_Number'] == patient_num].iloc[0].to_dict()
            else:
                return self.patient_data.iloc[0].to_dict()
        except Exception as e:
            print(e)
            return dict()
    
    def get_patient_record(self, patient_id= 1, row_num=0):
        if isinstance(patient_id, str):
            patient_id = int(patient_id)
        try:
            patient_num_in_db = patient_id in self.patient_data['Patient_Number'].unique()
            if patient_num_in_db:
                return self.patient_data[self.patient_data['Patient_Number'] == patient_id].iloc[0].to_dict()
            else:
                return self.patient_data.iloc[0].to_dict()
        except Exception as e:
            print(e)
            return dict()


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
    
def get_patient_data_metadata():
    file1 = '/mnt/f/chat_ui/data/health_schema.xlsx'
    file2 = '/mnt/f/chat_ui/data/activity_schema.xlsx'

    health_metadata = MetaDataManager(file1)
    activity_metadata = MetaDataManager(file2)

    output = []
    output.append(f'DataFrame name -> health')
    output.append(f'Column Name & Description -')
    output.append(health_metadata.get_column_descriptions(as_text=True))
    output.append('\n')
    output.append(f'DataFrame name -> activity')
    output.append(f'Column Name & Description -')
    output.append(activity_metadata.get_column_descriptions(as_text=True))    
    return '\n'.join(output)
    
def test():
        file1 = '/mnt/f/chat_ui/data/health_schema.xlsx'
        file2 = '/mnt/f/chat_ui/data/activity_schema.xlsx'

        health_metadata = MetaDataManager(file1)
        activity_metadata = MetaDataManager(file2)

        print(health_metadata.get_column_descriptions(as_text=True))
        print(10*'=')
        print(activity_metadata.get_column_descriptions(as_text=True))

if __name__ == '__main__':
    print(get_patient_data_metadata())