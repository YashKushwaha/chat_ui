import requests

def get_model_list():
    url = 'http://localhost:11434/api/tags'
    response = requests.get(url)
    if response.status_code == 200:
        model_json = response.json()
        models = model_json['models']
        model_list = [model['model'] for model in models]
        return model_list
    else:
        print(f'Server not responding at {url}. Status code received -> {response.status_code}')
        return []
    
#if __name__ == '__main__':
#    print(get_model_list())