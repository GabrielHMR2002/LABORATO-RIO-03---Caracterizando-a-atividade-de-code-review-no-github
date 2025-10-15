import requests
import pandas as pd
import time
from datetime import datetime, timedelta

class GitHubPRCollector:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
    
    def get_popular_repositories(self, limit=200):
        repos = []
        page = 1
        per_page = 100
        
        print(f"Coletando top {limit} repositórios populares...")
        
        while len(repos) < limit:
            url = f"{self.base_url}/search/repositories"
            params = {
                'q': 'stars:>1000',
                'sort': 'stars',
                'order': 'desc',
                'per_page': per_page,
                'page': page
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                repos.extend(data['items'])
                print(f"Coletados {len(repos)} repositórios...")
                
                if len(data['items']) < per_page:
                    break
                    
                page += 1
                time.sleep(2)
            else:
                print(f"Erro ao coletar repositórios: {response.status_code}")
                break
        
        return repos[:limit]
    
    def count_prs(self, owner, repo):
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {'state': 'closed', 'per_page': 1}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            if 'Link' in response.headers:
                links = response.headers['Link']
                if 'last' in links:
                    last_page = int(links.split('page=')[-1].split('>')[0])
                    return last_page
        return 0
    
    def filter_repositories(self, repos, min_prs=100):
        filtered = []
        
        print(f"\nFiltrando repositórios com pelo menos {min_prs} PRs...")
        
        for repo in repos:
            owner = repo['owner']['login']
            name = repo['name']
            
            pr_count = self.count_prs(owner, name)
            
            if pr_count >= min_prs:
                filtered.append({
                    'owner': owner,
                    'name': name,
                    'stars': repo['stargazers_count'],
                    'pr_count': pr_count
                })
                print(f"✓ {owner}/{name}: {pr_count} PRs")
            else:
                print(f"✗ {owner}/{name}: {pr_count} PRs (< {min_prs})")
            
            time.sleep(1)
        
        return filtered
    
    def get_pr_reviews(self, owner, repo, pr_number):
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else []
    
    def get_pr_comments(self, owner, repo, pr_number):
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else []
    
    def get_issue_comments(self, owner, repo, pr_number):
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else []
    
    def collect_prs_from_repo(self, owner, repo, max_prs=200):
        prs_data = []
        page = 1
        per_page = 100
        
        print(f"\nColetando PRs de {owner}/{repo}...")
        
        while len(prs_data) < max_prs:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            params = {
                'state': 'closed',
                'per_page': per_page,
                'page': page,
                'sort': 'created',
                'direction': 'desc'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Erro ao coletar PRs: {response.status_code}")
                break
            
            prs = response.json()
            if not prs:
                break
            
            for pr in prs:
                try:
                    if not all(key in pr for key in ['number', 'created_at', 'user']):
                        continue
                    
                    pr_url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr['number']}"
                    pr_response = requests.get(pr_url, headers=self.headers)
                    
                    if pr_response.status_code != 200:
                        continue
                    
                    pr_full = pr_response.json()
                    time.sleep(0.5)
                    
                    required_fields = ['changed_files', 'additions', 'deletions', 
                                      'created_at', 'user', 'body']
                    if not all(key in pr_full for key in required_fields):
                        continue
                    
                    reviews = self.get_pr_reviews(owner, repo, pr['number'])
                    time.sleep(0.5)
                    
                    if len(reviews) < 1:
                        continue
                    
                    created_at = datetime.strptime(pr_full['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                    
                    if pr_full.get('merged_at'):
                        closed_at = datetime.strptime(pr_full['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
                        status = 'MERGED'
                    elif pr_full.get('closed_at'):
                        closed_at = datetime.strptime(pr_full['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
                        status = 'CLOSED'
                    else:
                        continue
                    
                    time_diff = closed_at - created_at
                    if time_diff < timedelta(hours=1):
                        continue
                    
                    pr_comments = self.get_pr_comments(owner, repo, pr['number'])
                    issue_comments = self.get_issue_comments(owner, repo, pr['number'])
                    time.sleep(0.5)
                    
                    participants = set()
                    if pr_full.get('user') and pr_full['user'].get('login'):
                        participants.add(pr_full['user']['login'])
                    
                    for review in reviews:
                        if review.get('user') and review['user'].get('login'):
                            participants.add(review['user']['login'])
                    
                    for comment in pr_comments + issue_comments:
                        if comment.get('user') and comment['user'].get('login'):
                            participants.add(comment['user']['login'])
                    
                    pr_data = {
                        'repo_owner': owner,
                        'repo_name': repo,
                        'pr_number': pr_full['number'],
                        'status': status,
                        'created_at': pr_full['created_at'],
                        'closed_at': pr_full.get('merged_at') or pr_full.get('closed_at'),
                        'files_changed': pr_full.get('changed_files', 0),
                        'additions': pr_full.get('additions', 0),
                        'deletions': pr_full.get('deletions', 0),
                        'total_lines_changed': pr_full.get('additions', 0) + pr_full.get('deletions', 0),
                        'body_length': len(pr_full['body']) if pr_full.get('body') else 0,
                        'num_reviews': len(reviews),
                        'num_comments': len(pr_comments) + len(issue_comments),
                        'num_participants': len(participants),
                        'time_to_close_hours': time_diff.total_seconds() / 3600
                    }
                    
                    prs_data.append(pr_data)
                    
                except Exception as e:
                    continue
                
                if len(prs_data) >= max_prs:
                    break
            
            print(f"Coletados {len(prs_data)} PRs válidos até agora...")
            page += 1
            time.sleep(2)
            
            if len(prs) < per_page:
                break
        
        return prs_data
    
    def save_repositories(self, repos, filename='selected_repositories.csv'):
        df = pd.DataFrame(repos)
        df.to_csv(filename, index=False)
        print(f"\nRepositórios salvos em {filename}")
        return df
    
    def save_dataset(self, data, filename='github_prs_dataset.csv'):
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"\nDataset salvo em {filename} com {len(df)} PRs")
        return df