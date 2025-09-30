# 1_selecionar_repositorios.py

import requests
import json
import time
from datetime import datetime

GITHUB_TOKEN = "seu_token_aqui"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def buscar_repositorios_populares(quantidade=200):
    repositorios = []
    por_pagina = 100
    paginas_necessarias = (quantidade + por_pagina - 1) // por_pagina
    
    print(f"Buscando {quantidade} repositorios mais populares...")
    
    for pagina in range(1, paginas_necessarias + 1):
        url = f"https://api.github.com/search/repositories"
        params = {
            "q": "stars:>1",
            "sort": "stars",
            "order": "desc",
            "per_page": por_pagina,
            "page": pagina
        }
        
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            
            dados = response.json()
            repositorios.extend(dados['items'])
            
            print(f"Pagina {pagina}/{paginas_necessarias} - Coletados {len(repositorios)} repositorios")
            
            time.sleep(2)
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar repositorios: {e}")
            break
    
    return repositorios[:quantidade]

def contar_prs_repositorio(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    
    total_prs = 0
    
    params = {
        "state": "closed",
        "per_page": 1
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        
        if 'Link' in response.headers:
            links = response.headers['Link']
            import re
            matches = re.findall(r'page=(\d+)>; rel="last"', links)
            if matches:
                total_prs = int(matches[0])
        
        if total_prs == 0:
            search_url = f"https://api.github.com/search/issues"
            search_params = {
                "q": f"repo:{owner}/{repo} type:pr is:closed",
                "per_page": 1
            }
            response = requests.get(search_url, headers=HEADERS, params=search_params)
            response.raise_for_status()
            total_prs = response.json().get('total_count', 0)
        
        return total_prs
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao contar PRs de {owner}/{repo}: {e}")
        return 0

def filtrar_repositorios_com_prs(repositorios, min_prs=100):
    repos_filtrados = []
    
    print(f"\nFiltrando repositorios com pelo menos {min_prs} PRs...")
    
    for i, repo in enumerate(repositorios, 1):
        owner = repo['owner']['login']
        nome = repo['name']
        
        print(f"[{i}/{len(repositorios)}] Verificando {owner}/{nome}...", end=" ")
        
        total_prs = contar_prs_repositorio(owner, nome)
        
        if total_prs >= min_prs:
            repo_info = {
                'owner': owner,
                'name': nome,
                'full_name': repo['full_name'],
                'stars': repo['stargazers_count'],
                'total_prs': total_prs,
                'language': repo.get('language', 'N/A'),
                'url': repo['html_url']
            }
            repos_filtrados.append(repo_info)
            print(f"{total_prs} PRs")
        else:
            print(f"{total_prs} PRs (insuficiente)")
        
        time.sleep(1)
    
    return repos_filtrados

def salvar_repositorios(repositorios, arquivo='repositorios_selecionados.json'):
    dados = {
        'data_coleta': datetime.now().isoformat(),
        'total_repositorios': len(repositorios),
        'repositorios': repositorios
    }
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    print(f"\n{len(repositorios)} repositorios salvos em {arquivo}")

def main():
    print("SELECAO DE REPOSITORIOS - LAB03S01")
    
    repositorios = buscar_repositorios_populares(200)
    print(f"\n{len(repositorios)} repositorios populares coletados")
    
    repos_filtrados = filtrar_repositorios_com_prs(repositorios, min_prs=100)
    
    salvar_repositorios(repos_filtrados)
    
    print("\nRESUMO:")
    print(f"Repositorios analisados: {len(repositorios)}")
    print(f"Repositorios selecionados: {len(repos_filtrados)}")

if __name__ == "__main__":
    main()