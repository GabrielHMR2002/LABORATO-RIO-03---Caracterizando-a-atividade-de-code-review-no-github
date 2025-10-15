"""
Pipeline Principal - LAB03: Caracterizando a atividade de code review no GitHub

Este script integra todas as etapas do laboratório:
1. Coleta de dados do GitHub
2. Análise estatística
3. Geração de visualizações
4. Geração de relatório

Autor: [Seu Nome]
Data: [Data]
"""

import os
import sys
from datetime import datetime
import pandas as pd
import json

class LabPipeline:
    
    def __init__(self, github_token, output_dir='lab03_output'):
        self.token = github_token
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.create_directories()
        
        print("=" * 80)
        print("LAB03 - Pipeline de Análise de Code Review no GitHub")
        print("=" * 80)
        print(f"Diretório de saída: {self.output_dir}")
        print(f"Timestamp: {self.timestamp}\n")
    
    def create_directories(self):
        dirs = [
            self.output_dir,
            f"{self.output_dir}/data",
            f"{self.output_dir}/plots",
            f"{self.output_dir}/reports"
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def step1_collect_repositories(self, limit=200, min_prs=100):

        print("\n" + "=" * 80)
        print("ETAPA 1: Coleta e Filtragem de Repositórios")
        print("=" * 80)
        
        from github_pr_collector import GitHubPRCollector
        
        collector = GitHubPRCollector(self.token)
        
        print(f"\n[1/2] Coletando top {limit} repositórios populares...")
        popular_repos = collector.get_popular_repositories(limit=limit)
        
        print(f"\n[2/2] Filtrando repositórios com pelo menos {min_prs} PRs...")
        filtered_repos = collector.filter_repositories(popular_repos, min_prs=min_prs)
        
        repos_file = f"{self.output_dir}/data/selected_repositories_{self.timestamp}.csv"
        repos_df = collector.save_repositories(filtered_repos, filename=repos_file)
        
        print(f"\n✓ Etapa 1 concluída!")
        print(f"  - Total de repositórios selecionados: {len(filtered_repos)}")
        print(f"  - Arquivo salvo: {repos_file}")
        
        return filtered_repos, repos_df
    
    def step2_collect_prs(self, repositories, max_prs_per_repo=100, max_repos=None):

        print("\n" + "=" * 80)
        print("ETAPA 2: Coleta de Pull Requests e Métricas")
        print("=" * 80)
        
        from github_pr_collector import GitHubPRCollector
        
        collector = GitHubPRCollector(self.token)
        
        all_prs = []
        repos_to_process = repositories[:max_repos] if max_repos else repositories
        
        total_repos = len(repos_to_process)
        
        for idx, repo in enumerate(repos_to_process, 1):
            print(f"\n[{idx}/{total_repos}] Processando {repo['owner']}/{repo['name']}...")
            
            try:
                prs = collector.collect_prs_from_repo(
                    repo['owner'], 
                    repo['name'], 
                    max_prs=max_prs_per_repo
                )
                all_prs.extend(prs)
                print(f"  ✓ Coletados {len(prs)} PRs")
            except Exception as e:
                print(f"  ✗ Erro ao processar repositório: {e}")
                continue
            
            if idx % 5 == 0:
                checkpoint_file = f"{self.output_dir}/data/checkpoint_{idx}_repos.csv"
                pd.DataFrame(all_prs).to_csv(checkpoint_file, index=False)
                print(f"  → Checkpoint salvo: {checkpoint_file}")
        
        dataset_file = f"{self.output_dir}/data/github_prs_dataset_{self.timestamp}.csv"
        dataset_df = collector.save_dataset(all_prs, filename=dataset_file)
        
        print(f"\n✓ Etapa 2 concluída!")
        print(f"  - Total de PRs coletados: {len(all_prs)}")
        print(f"  - Arquivo salvo: {dataset_file}")
        
        return dataset_df, dataset_file
    
    def step3_analyze_data(self, dataset_file):

        print("\n" + "=" * 80)
        print("ETAPA 3: Análise Estatística")
        print("=" * 80)
        
        from statistical_analysis import PRAnalyzer
        
        analyzer = PRAnalyzer(dataset_file)
        
        print("\nExecutando análises para todas as RQs...")
        results = analyzer.run_all_analyses()
        
        results_file = f"{self.output_dir}/reports/analysis_results_{self.timestamp}.json"
        
        serializable_results = {}
        for rq, data in results.items():
            serializable_results[rq] = {}
            for key, value in data.items():
                if isinstance(value, pd.DataFrame):
                    serializable_results[rq][key] = value.to_dict()
                else:
                    serializable_results[rq][key] = value
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        report_file = f"{self.output_dir}/reports/analysis_results_{self.timestamp}.txt"
        analyzer.generate_report(output_file=report_file)
        
        print(f"\n✓ Etapa 3 concluída!")
        print(f"  - Resultados JSON: {results_file}")
        print(f"  - Relatório textual: {report_file}")
        
        return analyzer, results
    
    def step4_generate_visualizations(self, dataset_file):

        print("\n" + "=" * 80)
        print("ETAPA 4: Geração de Visualizações")
        print("=" * 80)
        
        from data_visualization import PRVisualizer
        
        plots_dir = f"{self.output_dir}/plots/{self.timestamp}"
        os.makedirs(plots_dir, exist_ok=True)
        
        visualizer = PRVisualizer(dataset_file)
        
        print("\nGerando gráficos...")
        
        visualizer.plot_status_distribution(f"{plots_dir}/01_status_distribution.png")
        visualizer.plot_size_comparison(f"{plots_dir}/02_size_comparison.png")
        visualizer.plot_time_analysis(f"{plots_dir}/03_time_analysis.png")
        visualizer.plot_description_analysis(f"{plots_dir}/04_description_analysis.png")
        visualizer.plot_interactions_analysis(f"{plots_dir}/05_interactions_analysis.png")
        visualizer.plot_reviews_vs_size(f"{plots_dir}/06_reviews_vs_size.png")
        visualizer.plot_reviews_vs_time(f"{plots_dir}/07_reviews_vs_time.png")
        visualizer.plot_reviews_vs_description(f"{plots_dir}/08_reviews_vs_description.png")
        visualizer.plot_reviews_vs_interactions(f"{plots_dir}/09_reviews_vs_interactions.png")
        visualizer.plot_correlation_heatmap(f"{plots_dir}/10_correlation_heatmap.png")
        
        print(f"\n✓ Etapa 4 concluída!")
        print(f"  - Gráficos salvos em: {plots_dir}")
        print(f"  - Total de visualizações: 10")
        
        return plots_dir
    
    def step5_generate_final_report(self, dataset_file, analyzer, results, plots_dir):
        """
        Etapa 5: Gerar relatório final em formato markdown
        Lab03S02 + Lab03S03: Relatório final (5 + 10 pontos)
        """
        print("\n" + "=" * 80)
        print("ETAPA 5: Geração do Relatório Final")
        print("=" * 80)
        
        df = pd.read_csv(dataset_file)
        
        report_file = f"{self.output_dir}/reports/relatorio_final_{self.timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("# Relatório Final - LAB03\n")
            f.write("## Caracterizando a atividade de code review no GitHub\n\n")
            f.write(f"**Data:** {datetime.now().strftime('%d/%m/%Y')}\n\n")
            f.write("---\n\n")
            
            # Estatísticas gerais
            f.write("## 1. Visão Geral do Dataset\n\n")
            f.write(f"- **Total de PRs analisados:** {len(df)}\n")
            f.write(f"- **PRs MERGED:** {sum(df['status'] == 'MERGED')} ({sum(df['status'] == 'MERGED')/len(df)*100:.1f}%)\n")
            f.write(f"- **PRs CLOSED:** {sum(df['status'] == 'CLOSED')} ({sum(df['status'] == 'CLOSED')/len(df)*100:.1f}%)\n\n")
            
            # Estatísticas descritivas
            f.write("### Medianas das Métricas\n\n")
            f.write("| Métrica | Geral | MERGED | CLOSED |\n")
            f.write("|---------|-------|--------|--------|\n")
            
            metrics = {
                'Arquivos Alterados': 'files_changed',
                'Linhas Adicionadas': 'additions',
                'Linhas Removidas': 'deletions',
                'Total de Linhas': 'total_lines_changed',
                'Tempo (horas)': 'time_to_close_hours',
                'Descrição (caracteres)': 'body_length',
                'Participantes': 'num_participants',
                'Comentários': 'num_comments',
                'Revisões': 'num_reviews'
            }
            
            for label, column in metrics.items():
                overall = df[column].median()
                merged = df[df['status'] == 'MERGED'][column].median()
                closed = df[df['status'] == 'CLOSED'][column].median()
                f.write(f"| {label} | {overall:.1f} | {merged:.1f} | {closed:.1f} |\n")
            
            f.write("\n---\n\n")
            
            # Resultados das RQs
            f.write("## 2. Resultados das Questões de Pesquisa\n\n")
            
            # RQ01-RQ04 (Status)
            status_rqs = ['RQ01', 'RQ02', 'RQ03', 'RQ04']
            for rq in status_rqs:
                if rq in results:
                    f.write(f"### {rq}\n\n")
                    
                    if 'correlations' in results[rq]:
                        f.write("| Métrica | Correlação (ρ) | p-value | Significante |\n")
                        f.write("|---------|---------------|---------|-------------|\n")
                        for var, corr in results[rq]['correlations'].items():
                            sig = "Sim ✓" if corr['significant'] else "Não ✗"
                            f.write(f"| {var} | {corr['correlation']:.4f} | {corr['p_value']:.6f} | {sig} |\n")
                    elif 'correlation' in results[rq]:
                        corr = results[rq]['correlation']
                        f.write(f"- **Correlação (ρ):** {corr['correlation']:.4f}\n")
                        f.write(f"- **p-value:** {corr['p_value']:.6f}\n")
                        f.write(f"- **Significante:** {'Sim ✓' if corr['significant'] else 'Não ✗'}\n")
                    
                    f.write("\n")
            
            f.write("---\n\n")
            
            # RQ05-RQ08 (Revisões)
            review_rqs = ['RQ05', 'RQ06', 'RQ07', 'RQ08']
            for rq in review_rqs:
                if rq in results:
                    f.write(f"### {rq}\n\n")
                    
                    if 'correlations' in results[rq]:
                        f.write("| Métrica | Correlação (ρ) | p-value | Significante |\n")
                        f.write("|---------|---------------|---------|-------------|\n")
                        for var, corr in results[rq]['correlations'].items():
                            sig = "Sim ✓" if corr['significant'] else "Não ✗"
                            f.write(f"| {var} | {corr['correlation']:.4f} | {corr['p_value']:.6f} | {sig} |\n")
                    elif 'correlation' in results[rq]:
                        corr = results[rq]['correlation']
                        f.write(f"- **Correlação (ρ):** {corr['correlation']:.4f}\n")
                        f.write(f"- **p-value:** {corr['p_value']:.6f}\n")
                        f.write(f"- **Significante:** {'Sim ✓' if corr['significant'] else 'Não ✗'}\n")
                    
                    f.write("\n")
            
            f.write("---\n\n")
            
            f.write("## 3. Visualizações\n\n")
            f.write("As visualizações geradas encontram-se no diretório:\n")
            f.write(f"```\n{plots_dir}\n```\n\n")
            
            f.write("Lista de gráficos:\n")
            plots = [
                "01_status_distribution.png - Distribuição de Status",
                "02_size_comparison.png - RQ01: Tamanho vs Status",
                "03_time_analysis.png - RQ02: Tempo vs Status",
                "04_description_analysis.png - RQ03: Descrição vs Status",
                "05_interactions_analysis.png - RQ04: Interações vs Status",
                "06_reviews_vs_size.png - RQ05: Tamanho vs Revisões",
                "07_reviews_vs_time.png - RQ06: Tempo vs Revisões",
                "08_reviews_vs_description.png - RQ07: Descrição vs Revisões",
                "09_reviews_vs_interactions.png - RQ08: Interações vs Revisões",
                "10_correlation_heatmap.png - Matriz de Correlação"
            ]
            
            for plot in plots:
                f.write(f"- `{plot}`\n")
            
            f.write("\n---\n\n")
            
            f.write("## 4. Conclusão\n\n")
            f.write("Este relatório apresenta os resultados da análise de code review em repositórios populares do GitHub. ")
            f.write("Os dados coletados e analisados fornecem insights importantes sobre os fatores que influenciam ")
            f.write("o merge de Pull Requests e o número de revisões necessárias.\n\n")
            f.write("Para uma análise completa e discussão detalhada dos resultados, consulte o template de relatório fornecido.\n\n")
        
        print(f"\n✓ Etapa 5 concluída!")
        print(f"  - Relatório final salvo: {report_file}")
        
        return report_file
    
    def run_full_pipeline(self, limit_repos=200, min_prs=100, max_repos=10, max_prs_per_repo=100):
        """
        Executa o pipeline completo
        
        Parâmetros:
        - limit_repos: Número de repositórios populares a buscar
        - min_prs: Mínimo de PRs que um repositório deve ter
        - max_repos: Máximo de repositórios a processar (None = todos)
        - max_prs_per_repo: Máximo de PRs a coletar por repositório
        """
        
        start_time = datetime.now()
        
        try:
            # Etapa 1: Coletar repositórios
            repositories, repos_df = self.step1_collect_repositories(
                limit=limit_repos, 
                min_prs=min_prs
            )
            
            # Etapa 2: Coletar PRs
            dataset_df, dataset_file = self.step2_collect_prs(
                repositories,
                max_prs_per_repo=max_prs_per_repo,
                max_repos=max_repos
            )
            
            # Etapa 3: Análise estatística
            analyzer, results = self.step3_analyze_data(dataset_file)
            
            # Etapa 4: Visualizações
            plots_dir = self.step4_generate_visualizations(dataset_file)
            
            # Etapa 5: Relatório final
            report_file = self.step5_generate_final_report(
                dataset_file, 
                analyzer, 
                results, 
                plots_dir
            )
            
            # Sumário final
            end_time = datetime.now()
            duration = end_time - start_time
            
            print("\n" + "=" * 80)
            print("PIPELINE CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print(f"\n⏱️  Tempo total de execução: {duration}")
            print(f"\n📁 Arquivos gerados:")
            print(f"   - Repositórios: {self.output_dir}/data/selected_repositories_{self.timestamp}.csv")
            print(f"   - Dataset: {dataset_file}")
            print(f"   - Análises: {self.output_dir}/reports/analysis_results_{self.timestamp}.txt")
            print(f"   - Visualizações: {plots_dir}")
            print(f"   - Relatório Final: {report_file}")
            
            print(f"\n✅ Todos os arquivos foram salvos em: {self.output_dir}/")
            print("\n" + "=" * 80 + "\n")
            
            return {
                'repositories': repositories,
                'dataset_file': dataset_file,
                'results': results,
                'plots_dir': plots_dir,
                'report_file': report_file
            }
            
        except Exception as e:
            print(f"\n❌ ERRO no pipeline: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Função principal para execução do laboratório"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    LAB03 - Code Review no GitHub                            ║
║                    Laboratório de Experimentação de Software                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("CONFIGURAÇÃO DO PIPELINE\n")
    print("Para executar este laboratório, você precisa:")
    print("1. Um token de acesso do GitHub")
    print("   → Gere em: https://github.com/settings/tokens")
    print("   → Permissões necessárias: public_repo, read:user")
    print("\n2. As bibliotecas Python instaladas:")
    print("   → pip install requests pandas scipy matplotlib seaborn numpy")
    print("\n" + "-" * 80 + "\n")
    
    github_token = input("Digite seu token do GitHub (ou pressione Enter para usar variável de ambiente): ").strip()
    
    if not github_token:
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("\n❌ Token não fornecido. Configure a variável GITHUB_TOKEN ou forneça o token.")
            return
    
    print("\n✓ Token configurado!")
    
    print("\n" + "-" * 80)
    print("PARÂMETROS DO PIPELINE")
    print("-" * 80 + "\n")
    
    print("Configuração padrão (recomendada para testes):")
    print("  - Top 200 repositórios mais populares")
    print("  - Mínimo 100 PRs por repositório")
    print("  - Processar 10 repositórios (para teste)")
    print("  - Coletar até 100 PRs por repositório")
    print()
    
    use_default = input("Usar configuração padrão? (s/n) [s]: ").strip().lower()
    
    if use_default == 'n':
        try:
            limit_repos = int(input("Limite de repositórios a buscar [200]: ") or "200")
            min_prs = int(input("Mínimo de PRs por repositório [100]: ") or "100")
            max_repos = input("Máximo de repositórios a processar [10] (deixe vazio para todos): ").strip()
            max_repos = int(max_repos) if max_repos else None
            max_prs_per_repo = int(input("Máximo de PRs por repositório [100]: ") or "100")
        except ValueError:
            print("❌ Valor inválido. Usando configuração padrão.")
            limit_repos, min_prs, max_repos, max_prs_per_repo = 200, 100, 10, 100
    else:
        limit_repos, min_prs, max_repos, max_prs_per_repo = 200, 100, 10, 100
    
    print("\n" + "=" * 80)
    print("INICIANDO PIPELINE")
    print("=" * 80)
    
    pipeline = LabPipeline(github_token=github_token)
    
    results = pipeline.run_full_pipeline(
        limit_repos=limit_repos,
        min_prs=min_prs,
        max_repos=max_repos,
        max_prs_per_repo=max_prs_per_repo
    )
    
    if results:
        print("\n🎉 Laboratório concluído com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. Revise os resultados no diretório de saída")
        print("   2. Analise as visualizações geradas")
        print("   3. Complete o relatório final com suas análises e discussões")
        print("   4. Utilize o template fornecido para estruturar seu documento")
    else:
        print("\n❌ Ocorreu um erro durante a execução do pipeline.")
        print("   Verifique os logs acima para mais informações.")


if __name__ == "__main__":
    main()