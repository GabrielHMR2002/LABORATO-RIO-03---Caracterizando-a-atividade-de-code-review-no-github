import pandas as pd
from scipy import stats

class PRAnalyzer:
    def __init__(self, dataset_path):
        self.df = pd.read_csv(dataset_path)
        self.results = {}
        self.df['status_numeric'] = (self.df['status'] == 'MERGED').astype(int)
        
        print(f"Dataset carregado: {len(self.df)} PRs")
        print(f"PRs MERGED: {sum(self.df['status'] == 'MERGED')}")
        print(f"PRs CLOSED: {sum(self.df['status'] == 'CLOSED')}")
    
    def calculate_correlation(self, var1, var2, method='spearman'):
        data = self.df[[var1, var2]].dropna()
        
        if method == 'spearman':
            corr, p_value = stats.spearmanr(data[var1], data[var2])
            method_name = "Spearman"
        else:
            corr, p_value = stats.pearsonr(data[var1], data[var2])
            method_name = "Pearson"
        
        return {
            'correlation': corr,
            'p_value': p_value,
            'method': method_name,
            'significant': p_value < 0.05
        }
    
    def get_summary_stats(self, column, group_by='status'):
        grouped = self.df.groupby(group_by)[column].describe()
        medians = self.df.groupby(group_by)[column].median()
        grouped['median'] = medians
        return grouped
    
    def analyze_rq01(self):
        print("\n=== RQ01: Tamanho dos PRs vs Feedback Final ===")
        results = {
            'files_changed': self.calculate_correlation('files_changed', 'status_numeric'),
            'additions': self.calculate_correlation('additions', 'status_numeric'),
            'deletions': self.calculate_correlation('deletions', 'status_numeric'),
            'total_lines': self.calculate_correlation('total_lines_changed', 'status_numeric')
        }
        self.results['RQ01'] = {'correlations': results}
        return results
    
    def analyze_rq02(self):
        print("\n=== RQ02: Tempo de Análise vs Feedback Final ===")
        result = self.calculate_correlation('time_to_close_hours', 'status_numeric')
        self.results['RQ02'] = {'correlation': result}
        return result
    
    def analyze_rq03(self):
        print("\n=== RQ03: Descrição dos PRs vs Feedback Final ===")
        result = self.calculate_correlation('body_length', 'status_numeric')
        self.results['RQ03'] = {'correlation': result}
        return result
    
    def analyze_rq04(self):
        print("\n=== RQ04: Interações vs Feedback Final ===")
        results = {
            'participants': self.calculate_correlation('num_participants', 'status_numeric'),
            'comments': self.calculate_correlation('num_comments', 'status_numeric')
        }
        self.results['RQ04'] = {'correlations': results}
        return results
    
    def analyze_rq05(self):
        print("\n=== RQ05: Tamanho dos PRs vs Número de Revisões ===")
        results = {
            'files_changed': self.calculate_correlation('files_changed', 'num_reviews'),
            'additions': self.calculate_correlation('additions', 'num_reviews'),
            'deletions': self.calculate_correlation('deletions', 'num_reviews'),
            'total_lines': self.calculate_correlation('total_lines_changed', 'num_reviews')
        }
        self.results['RQ05'] = {'correlations': results}
        return results
    
    def analyze_rq06(self):
        print("\n=== RQ06: Tempo de Análise vs Número de Revisões ===")
        result = self.calculate_correlation('time_to_close_hours', 'num_reviews')
        self.results['RQ06'] = {'correlation': result}
        return result
    
    def analyze_rq07(self):
        print("\n=== RQ07: Descrição dos PRs vs Número de Revisões ===")
        result = self.calculate_correlation('body_length', 'num_reviews')
        self.results['RQ07'] = {'correlation': result}
        return result
    
    def analyze_rq08(self):
        print("\n=== RQ08: Interações vs Número de Revisões ===")
        results = {
            'participants': self.calculate_correlation('num_participants', 'num_reviews'),
            'comments': self.calculate_correlation('num_comments', 'num_reviews')
        }
        self.results['RQ08'] = {'correlations': results}
        return results
    
    def run_all_analyses(self):
        print("Iniciando análises estatísticas...")
        self.analyze_rq01()
        self.analyze_rq02()
        self.analyze_rq03()
        self.analyze_rq04()
        self.analyze_rq05()
        self.analyze_rq06()
        self.analyze_rq07()
        self.analyze_rq08()
        print("\n=== ANÁLISES CONCLUÍDAS ===")
        return self.results
    
    def generate_report(self, output_file='analysis_results.txt'):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE ANÁLISE ESTATÍSTICA\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Total de PRs: {len(self.df)}\n")
            f.write(f"MERGED: {sum(self.df['status'] == 'MERGED')}\n")
            f.write(f"CLOSED: {sum(self.df['status'] == 'CLOSED')}\n\n")
            
            for rq in ['RQ01', 'RQ02', 'RQ03', 'RQ04', 'RQ05', 'RQ06', 'RQ07', 'RQ08']:
                f.write(f"\n{rq}\n")
                f.write("-" * 80 + "\n")
                
                if rq in self.results:
                    result = self.results[rq]
                    
                    if 'correlations' in result:
                        for var, corr in result['correlations'].items():
                            f.write(f"\n{var}:\n")
                            f.write(f"  Correlação: {corr['correlation']:.4f}\n")
                            f.write(f"  P-value: {corr['p_value']:.6f}\n")
                            f.write(f"  Significante: {'Sim' if corr['significant'] else 'Não'}\n")
                    
                    elif 'correlation' in result:
                        corr = result['correlation']
                        f.write(f"  Correlação: {corr['correlation']:.4f}\n")
                        f.write(f"  P-value: {corr['p_value']:.6f}\n")
                        f.write(f"  Significante: {'Sim' if corr['significant'] else 'Não'}\n")
        
        print(f"\nRelatório salvo em {output_file}")