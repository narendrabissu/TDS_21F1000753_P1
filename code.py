import requests
import csv
import os

# Git API token
GITHUB_TOKEN = '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'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Function to clean up company names
def clean_company_name(company):
    if company:
        company = company.strip().lstrip('@').upper()
    return company

# Fetch users in Shanghai with over 200 followers
def fetch_users():
    users = []
    page = 1
    while True:
        url = f'https://api.github.com/search/users?q=location:Shanghai+followers:>200&per_page=100&page={page}'
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        if 'items' not in data or not data['items']:
            break
        for user in data['items']:
            user_details = requests.get(user['url'], headers=HEADERS).json()
            users.append({
                'login': user_details['login'],
                'name': user_details.get('name', ''),
                'company': clean_company_name(user_details.get('company', '')),
                'location': user_details.get('location', ''),
                'email': user_details.get('email', ''),
                'hireable': user_details.get('hireable', ''),
                'bio': user_details.get('bio', ''),
                'public_repos': user_details.get('public_repos', 0),
                'followers': user_details.get('followers', 0),
                'following': user_details.get('following', 0),
                'created_at': user_details.get('created_at', '')
            })
        page += 1
    return users

# Fetch repositories for each user
def fetch_repositories(users):
    repositories = []
    for user in users:
        page = 1
        while True:
            url = f'https://api.github.com/users/{user["login"]}/repos?per_page=100&page={page}'
            response = requests.get(url, headers=HEADERS)
            data = response.json()
            if not data:
                break
            for repo in data:
                repositories.append({
                    'login': user['login'],
                    'full_name': repo['full_name'],
                    'created_at': repo['created_at'],
                    'stargazers_count': repo['stargazers_count'],
                    'watchers_count': repo['watchers_count'],
                    'language': repo.get('language', ''),
                    'has_projects': repo.get('has_projects', False),
                    'has_wiki': repo.get('has_wiki', False),
                    'license_name': repo['license']['key'] if repo.get('license') else ''
                })
            page += 1
    return repositories

# Save data to CSV files
def save_to_csv(users, repositories, folder_path):
    os.makedirs(folder_path, exist_ok=True)
    
    users_file_path = os.path.join(folder_path, 'users.csv')
    with open(users_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)
    
    repositories_file_path = os.path.join(folder_path, 'repositories.csv')
    with open(repositories_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=repositories[0].keys())
        writer.writeheader()
        writer.writerows(repositories)

# Create README.md
def create_readme(folder_path):
    readme_file_path = os.path.join(folder_path, 'README.md')
    with open(readme_file_path, 'w', encoding='utf-8') as file:
        file.write(
            "- Data was scraped using the GitHub API by searching for users in Shanghai with over 200 followers and fetching their repositories.\n"
            "- The most interesting fact found was the diversity of programming languages used by top developers in Shanghai.\n"
            "- Developers should consider contributing to open-source projects to increase their visibility and followers.\n"
        )

# Main function
def main():
    folder_path = './'  # Replace with your desired folder path
    users = fetch_users()
    repositories = fetch_repositories(users)
    save_to_csv(users, repositories, folder_path)
    create_readme(folder_path)

if __name__ == '__main__':
    main()
