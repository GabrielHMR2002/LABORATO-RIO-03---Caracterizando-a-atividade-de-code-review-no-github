import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.PRAnalyzer import PRAnalyzer
from src.PRVisualizer import PRVisualizer


def main():
    print("=" * 80)
    print("LAB03 - TESTE RÁPIDO (Dados Sintéticos)")
    print("=" * 80)
    
    # 1. GERAR DADOS
    print("\n[1/3] Gerando dados sintéticos...")
    
    os.makedirs('test_output', exist_ok=True)
    
    np.random.seed(42)
    n_prs = 500
    
    data = {
        'repo_owner': ['test'] * n_prs,
        'repo_name': ['repo'] * n_prs,
        'pr_number': range(1, n_prs + 1),
        'status': np.random.choice(['MERGED', 'CLOSED'], n_prs, p=[0.7, 0.3]),
        'created_at': ['2024-01-01T00:00:00Z'] * n_prs,
        'closed_at': ['2024-01-02T00:00:00Z'] * n_prs,
        'files_changed': np.random.poisson(5, n_prs) + 1,
        'additions': np.random.poisson(100, n_prs) + 10,
        'deletions': np.random.poisson(50, n_prs) + 5,
        'total_lines_changed': 0,
        'body_length': np.random.poisson(500, n_prs) + 50,
        'num_reviews': np.random.poisson(2, n_prs) + 1,
        'num_comments': np.random.poisson(5, n_prs),
        'num_participants': np.random.poisson(3, n_prs) + 1,
        'time_to_close_hours': np.random.exponential(24, n_prs) + 1
    }
    
    df = pd.DataFrame(data)
    df['total_lines_changed'] = df['additions'] + df['deletions']
    
    dataset_file = 'test_output/synthetic_dataset.csv'
    df.to_csv(dataset_file, index=False)
    
    print(f"✓ {len(df)} PRs gerados")
    print(f"  • MERGED: {sum(df['status'] == 'MERGED')}")
    print(f"  • CLOSED: {sum(df['status'] == 'CLOSED')}")
    
    # 2. ANÁLISE
    print("\n[2/3] Executando análise...")
    
    analyzer = PRAnalyzer(dataset_file)
    results = analyzer.run_all_analyses()
    analyzer.generate_report('test_output/analysis.txt')
    
    # 3. VISUALIZAÇÕES
    print("\n[3/3] Gerando gráficos...")
    
    visualizer = PRVisualizer(dataset_file)
    visualizer.generate_all_plots('test_output/plots')
    
    # RESULTADO
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 80)
    print("\n📁 Arquivos gerados:")
    print("   • test_output/synthetic_dataset.csv")
    print("   • test_output/analysis.txt")
    print("   • test_output/plots/")
    print("\n✅ Tudo funcionando! Agora você pode executar main.py com dados reais.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()