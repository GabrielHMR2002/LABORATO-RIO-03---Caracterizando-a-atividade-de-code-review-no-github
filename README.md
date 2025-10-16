# LABORATO-RIO-03---Caracterizando-a-atividade-de-code-review-no-github

# Análise Estatística de Pull Requests do GitHub

Estudo exploratório de 18.903 Pull Requests coletados do GitHub, investigando padrões e correlações entre características técnicas e sociais que influenciam a aceitação ou rejeição de contribuições.

## Objetivo

Este projeto analisa Pull Requests de repositórios do GitHub para identificar:
- Diferenças estatísticas entre PRs aceitos (merged) e rejeitados (closed)
- Correlações entre métricas técnicas (linhas de código, arquivos) e sociais (participantes, comentários)
- Fatores que influenciam o tempo de análise e aceitação de contribuições

## Dataset

### Composição
- Total de PRs: 18.903
  - Aceitos (MERGED): 12.201 (64,5%)
  - Rejeitados (CLOSED): 6.702 (35,5%)

### Métricas Coletadas
- **numero_arquivos**: Quantidade de arquivos modificados
- **linhas_adicionadas**: Total de linhas de código adicionadas
- **linhas_removidas**: Total de linhas de código removidas
- **intervalo_analise_horas**: Tempo entre abertura e fechamento (horas)
- **num_participantes**: Quantidade de pessoas que interagiram
- **num_comentarios**: Total de comentários na revisão

## Principais Descobertas

### 1. Tempo é Crítico
- PRs Aceitos: Mediana de aproximadamente 5 horas
- PRs Rejeitados: Mediana de aproximadamente 38 horas
- Insight: Tempo de resposta é o principal discriminador entre aceitação e rejeição

### 2. Tamanho Não Discrimina
- Distribuições de linhas adicionadas/removidas são praticamente idênticas entre aceitos e rejeitados
- Mediana de ambos próxima a 1 arquivo e 6-7 linhas
- Insight: Qualidade e contexto superam quantidade

### 3. Correlações Importantes
- numero_arquivos e linhas_adicionadas: 0.70 (forte)
- num_participantes e num_comentarios: 0.56 (moderada)
- intervalo_analise e num_participantes: 0.37 (moderada)
- tamanho e tempo_analise: 0.09 (fraca)

### 4. Distribuição Assimétrica
- Aproximadamente 18.000 PRs concentrados próximos de zero linhas adicionadas
- Distribuição long-tailed com outliers extremos (até 3 milhões de linhas)
- Padrão típico de desenvolvimento incremental
  
## Metodologia

### Coleta de Dados
Os dados foram coletados através da API do GitHub, utilizando scripts Python para extração automatizada de informações sobre Pull Requests de repositórios selecionados.

### Análise Estatística
A análise foi conduzida em quatro etapas:
1. Análise Descritiva: Caracterização da distribuição dos PRs por status
2. Análise Comparativa: Boxplots para comparar distribuições entre grupos
3. Análise de Distribuição: Histogramas para examinar a distribuição geral
4. Análise de Correlação: Matriz de correlação de Spearman

A escolha do coeficiente de correlação de Spearman se justifica por sua robustez a outliers e por não assumir relações lineares.

## Recomendações Práticas

### Para Desenvolvedores
- Monitorar tempo de resposta: Se não houver feedback em 48h, considerar follow-up
- Focar na qualidade: Tamanho não é impedimento decisivo
- Documentar bem: Contexto claro aumenta chances de aceitação
- Responder rapidamente: Participação ativa acelera o processo

### Para Mantenedores
- Estabelecer SLAs: Comprometer-se com feedback em 24-48h
- Implementar políticas de timeout: Fechar PRs inativos após 30 dias
- Usar automação: Bots para lembrar revisões pendentes
- Documentar critérios: Diretrizes claras reduzem PRs inadequados

## Limitações

- Métricas quantitativas: Não captura qualidade do código ou aderência a padrões
- Ausência de contexto: Não considera tipo de projeto ou maturidade
- Correlação não implica causalidade: Observamos associações, não causalidade definitiva
- Heterogeneidade: PRs de diferentes repositórios com culturas distintas

## Compilar Relatório

```bash
pdflatex lab03.tex
pdflatex lab03.tex
```

## Referências

- Gousios, G., et al. (2015). Work practices and challenges in pull-based development. ICSE.
- Yu, Y., et al. (2015). Wait for it: Determinants of pull request evaluation latency on GitHub. MSR.
- Rahman, M. M., & Roy, C. K. (2014). An insight into the pull requests of GitHub. MSR.

## Autor

Gabriel Henrique  
Outubro de 2025

## Licença

Este projeto está sob a licença MIT.
