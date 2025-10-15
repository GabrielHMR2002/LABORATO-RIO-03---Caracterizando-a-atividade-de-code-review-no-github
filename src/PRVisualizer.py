import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class PRVisualizer:
    def __init__(self, dataset_path):
        self.df = pd.read_csv(dataset_path)
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        print(f"Dataset carregado: {len(self.df)} PRs")
    
    def plot_status_distribution(self, save_path='status_distribution.png'):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        status_counts = self.df['status'].value_counts()
        colors = ['#2ecc71', '#e74c3c']
        
        ax1.bar(status_counts.index, status_counts.values, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_title('Distribuição de Status', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Quantidade')
        ax1.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(status_counts.values):
            ax1.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        
        ax2.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
                colors=colors, startangle=90)
        ax2.set_title('Proporção', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo: {save_path}")
        plt.close()
    
    def plot_size_comparison(self, save_path='size_comparison.png'):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        metrics = ['files_changed', 'additions', 'deletions', 'total_lines_changed']
        titles = ['Arquivos', 'Adições', 'Remoções', 'Total Linhas']
        
        for ax, metric, title in zip(axes.flatten(), metrics, titles):
            data = [self.df[self.df['status'] == 'MERGED'][metric],
                    self.df[self.df['status'] == 'CLOSED'][metric]]
            
            bp = ax.boxplot(data, labels=['MERGED', 'CLOSED'], patch_artist=True)
            
            colors = ['#2ecc71', '#e74c3c']
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)
            
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
        
        plt.suptitle('RQ01: Tamanho vs Status', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo: {save_path}")
        plt.close()
    
    def plot_correlation_heatmap(self, save_path='correlation_heatmap.png'):
        metrics = ['files_changed', 'total_lines_changed', 'time_to_close_hours',
                  'body_length', 'num_participants', 'num_comments', 'num_reviews']
        
        corr_matrix = self.df[metrics].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=1, fmt='.3f', vmin=-1, vmax=1)
        
        plt.title('Matriz de Correlação', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo: {save_path}")
        plt.close()
    
    def generate_all_plots(self, output_dir='plots'):
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n=== Gerando visualizações ===\n")
        self.plot_status_distribution(f'{output_dir}/01_status_distribution.png')
        self.plot_size_comparison(f'{output_dir}/02_size_comparison.png')
        self.plot_correlation_heatmap(f'{output_dir}/03_correlation_heatmap.png')
        print("\n=== Visualizações concluídas ===")