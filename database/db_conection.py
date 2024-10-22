import chromadb

chroma_client = chromadb.HttpClient(host='10.10.100.110', port=8000)
collection = chroma_client.get_collection('propostas')


def get_neighbor_ids(ids):
    id_list = []
    for i in range(0, len(ids)):
        id_list.append([str(int(ids[i])-1), str(int(ids[i])), str(int(ids[i])+1)])
    
    return id_list


def get_neighbor_ids_results(ids, distances):
    results = []
    
    # Fazendo o col.get dinamicamente para cada id_X
    for i in range(0, len(ids)):
        resp = collection.get(ids=ids[i])  # Pega a resposta para cada grupo de IDs
        # Remover ids de propostas diferentes
        for i in [2, 0]:
            if resp['metadatas'][i]['candidato'] != resp['metadatas'][1]['candidato']:
                for key in ['ids', 'metadatas', 'documents']:
                    resp[key].pop(i)

        results.append(resp)  # Adiciona a resposta à lista

    for i, dist in zip(results, distances):
        i['distance_chunk_principal'] = dist
        
    return results


def get_documents(query: str, n_results: int = 5):
    # Padronização de tudo minusculo
    query = query.lower()
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results, 
    )
    
    # Pegar os ids e distâncias dos resultados
    ids = results['ids'][0]  
    id_list = get_neighbor_ids(ids)
    distances = results['distances'][0]
    
    results_list = get_neighbor_ids_results(id_list, distances)
    
    final_results = []
    for item in results_list:
        resposta = {}
        resposta['sq_candidato'] = item['metadatas'][0]['candidato']
        resposta['nome'] = item['metadatas'][0]['nome']
        resposta['municipio'] = item['metadatas'][0]['ue']
        resposta['estado'] = item['metadatas'][0]['uf']
        resposta['documento'] = ' '.join(item['documents'])
        resposta['distancia'] = item['distance_chunk_principal']
        # Cortar chunks muitos distantes
        if item['distance_chunk_principal'] < 0.30:
            final_results.append(resposta)
        
    return final_results