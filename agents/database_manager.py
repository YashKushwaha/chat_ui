import os
import pandas as pd

class MetaDataManager:
    def __init__(self, metadata_file = None):
        self.metadata_file = metadata_file
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
        
    def data_cleaning(self, df):
        new_df = df.copy().ffill()
        rows = []
        for _, temp in new_df.groupby('Variable'):
            temp = temp.astype(str)
            to_append = {col: "|".join(temp[col].unique()) for col in temp.columns}
            rows.append(to_append)
        cleaned_df = pd.DataFrame(rows)
        return cleaned_df

    def dict_to_text(self, dict_to_convert):
        rows = []
        for i,j in dict_to_convert.items(): 
            rows.append(f'{i} : {j}')
        return '\n'.join(rows)

class DataBaseManager:
    def __init__(self, data_folder):
        self.data_folder = data_folder
        #self.metadata_list = self.create_file_list(self.data_folder)
        self.metadata_dict = self.create_file_list(self.data_folder)

    def create_file_list(self, data_folder):
        file_list  = [i for i in os.listdir(data_folder) if i.endswith('.xlsx') and ('~' not in i)]  
        table_names = {i.split('_')[0] for i in file_list}
        #metadata_list = []
        metadata_dict = dict()
        for table_name in table_names:
            data_file = f'{table_name}_dataset.xlsx'
            schema_file = f'{table_name}_schema.xlsx'
            #record = dict(table_name=table_name)
            record = dict()
            if os.path.exists(os.path.join(data_folder, data_file)):
                record['data_file'] = os.path.join(data_folder, data_file)
            else:
                record['data_file'] = None

            if os.path.exists(os.path.join(data_folder, schema_file)):
                record['schema_file'] = os.path.join(data_folder, schema_file)
            else:
                record['schema_file'] = None

            metadata_dict[table_name] = record
            #metadata_list.append(record)
        
        return metadata_dict#metadata_list

    def get_database_schema(self):
        pass

    def __repr__(self):

        repr = []
        for table_name, _ in self.metadata_dict.items():
            rows = [table_name]
            rows += [f'{i} : {j}' for i,j in _.items()]
            rows = '\n'.join(rows)
            repr.append(rows)
        return '\n\n'.join(repr)


    def __repr__old(self):
        repr = []
        for i in self.metadata_list:
            rows = [f'{i} : {j}' for i,j in i.items()]
            rows = '\n'.join(rows)
            repr.append(rows)
        return '\n\n'.join(repr)

if __name__ == '__main__':
    data_folder = '/mnt/f/chat_ui/data'

    db = DataBaseManager(data_folder)
    print(db)
    """
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
    def get_patient_data_metadata():
        return '\n'.join(output)
    """