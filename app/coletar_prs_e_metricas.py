# 2_coletar_prs_e_metricas.py

import requests
import json
import time
import csv
from datetime import datetime, timedelta

GITHUB_TOKEN = "seu_token_aqui"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def carregar_repositorios(arquivo='repositorios_selecionados.json'):
    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    return dados['repositorios']

def obter_prs_repositorio(owner, repo, max_prs=500):
    prs = []
    pagina = 1
    
    while len(prs) < max_prs:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {
            "state": "closed",
            "per_page": 100,
            "page": pagina,
            "sort": "updated",
            "direction": "desc"
        }
        
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            
            prs_pagina = response.json()
            
            if not prs_pagina:
                break
            
            prs.extend(prs_pagina)
            pagina += 1
            
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar PRs: {e}")
            break
    
    return prs

def obter_reviews_pr(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar reviews: {e}")
        return []

def obter_comentarios_pr(owner, repo, pr_number):
    url_comments = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    url_review_comments = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
    
    comentarios = []
    
    try:
        response = requests.get(url_comments, headers=HEADERS)
        response.raise_for_status()
        comentarios.extend(response.json())
        
        time.sleep(0.3)
        
        response = requests.get(url_review_comments, headers=HEADERS)
        response.raise_for_status()
        comentarios.extend(response.json())
        
        return comentarios
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar comentarios: {e}")
        return []

def calcular_tempo_analise(created_at, closed_at):
    if not created_at or not closed_at:
        return 0
    
    criacao = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    fechamento = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ")
    
    diferenca = fechamento - criacao
    horas = diferenca.total_seconds() / 3600
    
    return horas

def obter_participantes(pr, comentarios, reviews):
    participantes = set()
    
    if pr.get('user'):
        participantes.add(pr['user']['login'])
    
    for comentario in comentarios:
        if comentario.get('user'):
            participantes.add(comentario['user']['login'])
    
    for review in reviews:
        if review.get('user'):
            participantes.add(review['user']['login'])
    
    return len(participantes)

def extrair_metricas_pr(pr, owner, repo):
    pr_number = pr['number']
    
    reviews = obter_reviews_pr(owner, repo, pr_number)
    time.sleep(0.3)
    
    comentarios = obter_comentarios_pr(owner, repo, pr_number)
    time.sleep(0.3)
    
    num_reviews = len(reviews)
    tempo_analise_horas = calcular_tempo_analise(pr['created_at'], pr['closed_at'])
    
    if num_reviews < 1:
        return None
    
    if tempo_analise_horas <= 1:
        return None
    
    status = "MERGED" if pr.get('merged_at') else "CLOSED"
    
    num_arquivos = pr.get('changed_files', 0)
    linhas_adicionadas = pr.get('additions', 0)
    linhas_removidas = pr.get('deletions', 0)
    total_linhas_modificadas = linhas_adicionadas + linhas_removidas
    
    body = pr.get('body') or ""
    num_caracteres_descricao = len(body)
    
    num_participantes = obter_participantes(pr, comentarios, reviews)
    num_comentarios = len(comentarios)
    
    metricas = {
        'repositorio': f"{owner}/{repo}",
        'pr_number': pr_number,
        'titulo': pr['title'],
        'status': status,
        'created_at': pr['created_at'],
        'closed_at': pr['closed_at'],
        'tempo_analise_horas': round(tempo_analise_horas, 2),
        'num_arquivos': num_arquivos,
        'linhas_adicionadas': linhas_adicionadas,
        'linhas_removidas': linhas_removidas,
        'total_linhas_modificadas': total_linhas_modificadas,
        'num_caracteres_descricao': num_caracteres_descricao,
        'num_reviews': num_reviews,
        'num_participantes': num_participantes,
        'num_comentarios': num_comentarios,
        'url': pr['html_url']
    }
    
    return metricas

def coletar_dados_repositorio(owner, repo, max_prs=500):
    print(f"\nColetando PRs de {owner}/{repo}...")
    
    prs = obter_prs_repositorio(owner, repo, max_prs)
    print(f"  {len(prs)} PRs encontrados")
    
    metricas_list = []
    
    for i, pr in enumerate(prs, 1):
        print(f"  Processando PR #{pr['number']} ({i}/{len(prs)})...", end="\r")
        
        metricas = extrair_metricas_pr(pr, owner, repo)
        
        if metricas:
            metricas_list.append(metricas)
        
        time.sleep(1)
    
    print(f"\n  {len(metricas_list)} PRs validos coletados")
    
    return metricas_list

def salvar_dataset_csv(dados, arquivo='dataset_prs.csv'):
    if not dados:
        print("Nenhum dado para salvar")
        return
    
    campos = [
        'repositorio', 'pr_number', 'titulo', 'status',
        'created_at', 'closed_at', 'tempo_analise_horas',
        'num_arquivos', 'linhas_adicionadas', 'linhas_removidas',
        'total_linhas_modificadas', 'num_caracteres_descricao',
        'num_reviews', 'num_participantes', 'num_comentarios', 'url'
    ]
    
    with open(arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados)
    
    print(f"\nDataset salvo em {arquivo}")

def salvar_dataset_json(dados, arquivo='dataset_prs.json'):
    dataset = {
        'data_coleta': datetime.now().isoformat(),
        'total_prs': len(dados),
        'prs': dados
    }
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Dataset salvo em {arquivo}")

def main():
    print("COLETA DE PRs E METRICAS - LAB03S01")
    
    repositorios = carregar_repositorios()
    print(f"\n{len(repositorios)} repositorios carregados")
    
    todos_dados = []
    
    for i, repo in enumerate(repositorios, 1):
        print(f"\n[{i}/{len(repositorios)}]", end=" ")
        
        dados_repo = coletar_dados_repositorio(
            repo['owner'],
            repo['name'],
            max_prs=500
        )
        
        todos_dados.extend(dados_repo)
        
        print(f"Total acumulado: {len(todos_dados)} PRs")
        
        if i % 10 == 0:
            salvar_dataset_csv(todos_dados, f'dataset_checkpoint_{i}.csv')
    
    salvar_dataset_csv(todos_dados)
    salvar_dataset_json(todos_dados)
    
    print("\nRESUMO:")
    print(f"Repositorios processados: {len(repositorios)}")
    print(f"Total de PRs coletados: {len(todos_dados)}")

if __name__ == "__main__":
    main()