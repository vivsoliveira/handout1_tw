'''def extract_route(req):
    cont = 0
    lista = []
    sembarra = ""
    lista = req.split("\n")
    lista[0] = lista[0].replace("GET ","")
    lista[0] = lista[0].replace("POST ","")
    lista[0] = lista[0].replace("DELETE ","")
    lista[0] = lista[0].replace(" HTTP/1.1","")
    for i in range(len(lista[0])):
        if lista[0][i] == "/" and cont!=1:
            cont = 1
        else:
            sembarra = sembarra + lista[0][i]
    return(sembarra)'''

def extract_route(req):
    #nao entendi o fatiamento, dar prints para entender!!!!!!!!!!!!!!!!
    return req.split()[1][1:] #a posicao 1 é a rota, estamos fazendo split com um espaço

#print(extract_route("GET /img/logo-getit.png HTTP/1.1\nHost: 0.0.0.0:8080\nConnection: keep-alive"))

def read_file(path):
    with open(path, 'rb') as file:  # para abrir o arquivo em modo de leitura binária. 
                                    #O conteúdo é lido e retornado como bytes.
        content = file.read()

    return content

import json
def load_data(file_json):

    with open("data/{0}".format(file_json), 'r') as file:  # para abrir o arquivo em modo de leitura binária. 
                                    #O conteúdo é lido e retornado como bytes.
        content = file.read()
        #print(json.loads(content)[0]["titulo"])
    return json.loads(content)
#print(load_data("notes.json"))

def load_template(file):
    with open(f"templates/{file}", 'r') as file:
        texto = file.read()
    return texto

def add_note_to_file(file_json,dic_notes):
    with open("data/{0}".format(file_json)) as arquivo:
        lista_de_dicionarios = json.load(arquivo)
    lista_de_dicionarios.append(dic_notes)
    with open("data/{0}".format(file_json), 'w') as file:
        return json.dump(lista_de_dicionarios, file, indent=2)
    

def build_response(body='', code=200, reason='OK', headers=''):
    # Constrói a resposta HTTP formatada
    response = f'HTTP/1.1 {code} {reason}\n'

    
    if headers:
        response += f'{headers}\n'
    else:
        response += f'{headers}'
        

    response += '\n'
    response += body

    return response.encode()