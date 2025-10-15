"""
LAB03 - Script Principal
Executa coleta e análise de PRs do GitHub
"""

import os
import sys
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.GitHubPRCollector import GitHubPRCollector
from src.PRAnalyzer import PRAnalyzer
from src.PRVisualizer import PRVisualizer


def main():
    print("=" * 80)
    print("LAB03 - Code Review no GitHub")
    print("=" * 80)
    
    # 1. CONFIGURAÇÃO
    token = input("\nDigite seu token do GitHub: ").strip()
    if not token:
        print("❌ Token obrigatório!")
        return
    
    print("\n✓ Token configurado!")
    
    # 2. PARÂMETROS
    print("\n" + "-" * 80)
    print("PARÂMETROS DA COLETA")
    print("-" * 80)
    
    try:
        num_repos = int(input("Quantos repositórios processar? [5]: ") or "5")
        prs_per_repo = int(input("Quantos PRs por repositório? [50]: ") or "50")
    except:
        num_repos, prs_per_repo = 5, 50
    
    # 3. CRIAR DIRETÓRIOS
    os.makedirs('output', exist_ok=True)
    os.makedirs('output/data', exist_ok=True)
    os.makedirs('output/plots', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 4. COLETA
    print("\n" + "=" * 80)
    print("ETAPA 1: Coletando Repositórios")
    print("=" * 80)
    
    collector = GitHubPRCollector(token)
    
    # Buscar repositórios populares
    popular = collector.get_popular_repositories(limit=50)
    filtered = collector.filter_repositories(popular, min_prs=100)
    
    repos_file = f'output/data/repositories_{timestamp}.csv'
    collector.save_repositories(filtered[:num_repos], repos_file)
    
    # 5. COLETAR PRs
    print("\n" + "=" * 80)
    print("ETAPA 2: Coletando Pull Requests")
    print("=" * 80)
    
    all_prs = []
    for i, repo in enumerate(filtered[:num_repos], 1):
        print(f"\n[{i}/{num_repos}] {repo['owner']}/{repo['name']}")
        try:
            prs = collector.collect_prs_from_repo(
                repo['owner'], 
                repo['name'], 
                max_prs=prs_per_repo
            )
            all_prs.extend(prs)
        except Exception as e:
            print(f"  ✗ Erro: {e}")
    
    dataset_file = f'output/data/dataset_{timestamp}.csv'
    collector.save_dataset(all_prs, dataset_file)
    
    # Verificar se coletou PRs
    if len(all_prs) == 0:
        print("\n❌ ERRO: Nenhum PR foi coletado!")
        print("Possíveis causas:")
        print("  • Token sem permissões adequadas")
        print("  • Rate limit atingido")
        print("  • Repositórios sem PRs que atendem os critérios")
        print("\nTente novamente com:")
        print("  • Menos repositórios")
        print("  • Token novo com permissões: public_repo, read:user")
        return
    
    # 6. ANÁLISE
    print("\n" + "=" * 80)
    print("ETAPA 3: Análise Estatística")
    print("=" * 80)
    
    analyzer = PRAnalyzer(dataset_file)
    results = analyzer.run_all_analyses()
    
    report_file = f'output/analysis_{timestamp}.txt'
    analyzer.generate_report(report_file)
    
    # 7. VISUALIZAÇÕES
    print("\n" + "=" * 80)
    print("ETAPA 4: Gerando Gráficos")
    print("=" * 80)
    
    visualizer = PRVisualizer(dataset_file)
    plot_dir = f'output/plots/{timestamp}'
    visualizer.generate_all_plots(plot_dir)
    
    # 8. RESUMO
    print("\n" + "=" * 80)
    print("✅ CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print(f"\n📁 Arquivos gerados:")
    print(f"   • Repositórios: {repos_file}")
    print(f"   • Dataset: {dataset_file}")
    print(f"   • Análise: {report_file}")
    print(f"   • Gráficos: {plot_dir}/")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário\n")
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()