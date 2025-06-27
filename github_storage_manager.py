import pandas as pd
import json
import base64
import io
import requests
from datetime import datetime, timedelta
import os

class GitHubDataManager:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPO_OWNER', 'your-username')
        self.repo_name = os.getenv('GITHUB_REPO_NAME', '5s-dashboard-data')
        self.branch = 'main'
        
        # GitHub API base URL
        self.api_base = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_filename(self, year_month):
        """Get file path"""
        return f"data/data_{year_month}.json"
    
    def save_data(self, year_month, df):
        """Save data to GitHub"""
        if not self.github_token:
            print("GitHub token not found, using local storage")
            return self._save_local_fallback(year_month, df)
        
        try:
            data_dict = df.to_dict('index')
            content = json.dumps(data_dict, ensure_ascii=False, indent=2)
            
            # Encode to base64
            content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            file_path = self.get_filename(year_month)
            
            # Check if file exists
            sha = self._get_file_sha(file_path)
            
            payload = {
                'message': f'Update 5S data for {year_month}',
                'content': content_encoded,
                'branch': self.branch
            }
            
            if sha:
                payload['sha'] = sha
            
            url = f"{self.api_base}/contents/{file_path}"
            response = requests.put(url, headers=self.headers, json=payload)
            
            if response.status_code in [200, 201]:
                print(f"Data saved to GitHub: {file_path}")
                return True
            else:
                print(f"Failed to save to GitHub: {response.status_code}")
                return self._save_local_fallback(year_month, df)
                
        except Exception as e:
            print(f"Error saving to GitHub: {e}")
            return self._save_local_fallback(year_month, df)
    
    def load_data(self, year_month):
        """Load data from GitHub"""
        print(f"Loading data for: {year_month}")
        
        if not self.github_token:
            print("Using local storage mode")
            return self._load_local_fallback(year_month)
        
        try:
            file_path = self.get_filename(year_month)
            url = f"{self.api_base}/contents/{file_path}"
            print(f"Request URL: {url}")
            
            response = requests.get(url, headers=self.headers)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                file_data = response.json()
                content = base64.b64decode(file_data['content']).decode('utf-8')
                data_dict = json.loads(content)
                df = pd.DataFrame.from_dict(data_dict, orient='index')
                print(f"Successfully loaded data: {len(df)} rows, {len(df.columns)} columns")
                return df
            else:
                print(f"File not found or no permission: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error loading data: {e}")
            return self._load_local_fallback(year_month)
    
    def data_exists(self, year_month):
        """Check if data exists"""
        if not self.github_token:
            return False
        
        try:
            file_path = self.get_filename(year_month)
            url = f"{self.api_base}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)
            return response.status_code == 200
        except:
            return False
    
    def get_available_months(self):
        """Get all available months"""
        if not self.github_token:
            return []
        
        try:
            url = f"{self.api_base}/contents/data"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                files = response.json()
                months = []
                for file in files:
                    if file['name'].startswith('data_') and file['name'].endswith('.json'):
                        month = file['name'][5:-5]  # Remove 'data_' and '.json'
                        months.append(month)
                
                months.sort(reverse=True)
                return months
            else:
                return []
                
        except Exception as e:
            print(f"Error getting months from GitHub: {e}")
            return []
    
    def _get_file_sha(self, file_path):
        """Get file SHA (for updating)"""
        try:
            url = f"{self.api_base}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()['sha']
        except:
            pass
        return None
    
    def _save_local_fallback(self, year_month, df):
        """Local storage fallback"""
        os.makedirs('dashboard_data', exist_ok=True)
        filename = f"dashboard_data/data_{year_month}.json"
        data_dict = df.to_dict('index')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
        return True
    
    def _load_local_fallback(self, year_month):
        """Local loading fallback"""
        filename = f"dashboard_data/data_{year_month}.json"
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data_dict = json.load(f)
            return pd.DataFrame.from_dict(data_dict, orient='index')
        return None

    def generate_month_options(self, start_year=2020, end_year=2040):
        """Generate month options - from January 2020 to December 2040"""
        current_date = datetime.now()
        current_year_month = current_date.strftime("%Y-%m")
        options = []
        
        # Generate all months from start_year to end_year
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                year_month = f"{year}-{month:02d}"
                month_name = f"{year}年{month:02d}月"
                
                # Mark current month
                if year_month == current_year_month:
                    label = f"{month_name} (當前)"
                else:
                    label = month_name
                
                options.append({'label': label, 'value': year_month})

        # Sort in reverse chronological order (newest first)
        options.reverse()

        return options  # FIXED: Added missing return statement

    def parse_excel_file(self, contents, filename):
        """Parse Excel file - ensure HK_avg and SC_avg exist"""
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            if 'xlsx' in filename or 'xls' in filename:
                df_uploaded = pd.read_excel(io.BytesIO(decoded))
            else:
                return None, "Please upload Excel file (.xlsx or .xls)"
            
            required_cols = ['Site', 'Monthly Performance', 'Max/Month', 'Completed', 'Missing', 
                            'Week 1', 'Week 2', 'Week 3', 'Week 4']
            
            if not all(col in df_uploaded.columns for col in required_cols):
                missing_cols = [col for col in required_cols if col not in df_uploaded.columns]
                return None, f"Missing required columns: {', '.join(missing_cols)}"
            
            df_uploaded = df_uploaded.set_index('Site')
            
            # Ensure HK_avg exists, add if missing


            if 'HK_avg' not in df_uploaded.index:
                default_row = {col: 0 for col in df_uploaded.columns}
                df_uploaded.loc['HK_avg'] = default_row
                print("Added missing Hong Kong Average with default values")  # CHANGED

            if 'SC_avg' not in df_uploaded.index:
                default_row = {col: 0 for col in df_uploaded.columns}
                df_uploaded.loc['SC_avg'] = default_row
                print("Added missing South China Average with default values")  # CHANGED
            
            return df_uploaded, "File uploaded successfully!"
            
        except Exception as e:
            return None, f"Error parsing file: {str(e)}"
    
    def delete_month_data(self, year_month):
        """Delete data for specified year-month"""
        if not self.github_token:
            return self._delete_local_fallback(year_month)
        
        try:
            file_path = self.get_filename(year_month)
            sha = self._get_file_sha(file_path)
            
            if not sha:
                return False, f"Data for {year_month} does not exist"
            
            payload = {
                'message': f'Delete 5S data for {year_month}',
                'sha': sha,
                'branch': self.branch
            }
            
            url = f"{self.api_base}/contents/{file_path}"
            response = requests.delete(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                return True, f"Deleted GitHub data for {year_month}"
            else:
                return False, f"Failed to delete GitHub data: {response.status_code}"
                
        except Exception as e:
            return False, f"Error deleting data: {str(e)}"
    
    def export_month_data(self, year_month):
        """Export data for specified year-month as Excel format"""
        df = self.load_data(year_month)
        
        if df is None:
            return None, f"Data for {year_month} does not exist"
        
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.reset_index().to_excel(writer, sheet_name=f'5S_Data_{year_month}', index=False)
            
            output.seek(0)
            
            return {
                'content': base64.b64encode(output.getvalue()).decode(),
                'filename': f"5S_Dashboard_{year_month}.xlsx",
                'type': "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                'base64': True
            }, "Export successful"
            
        except Exception as e:
            return None, f"Error exporting data: {str(e)}"
    
    def _delete_local_fallback(self, year_month):
        """Local deletion fallback"""
        filename = f"dashboard_data/data_{year_month}.json"
        if os.path.exists(filename):
            try:
                os.remove(filename)
                return True, f"Deleted local data for {year_month}"
            except Exception as e:
                return False, f"Error deleting local data: {str(e)}"
        else:
            return False, f"Local data for {year_month} does not exist"
        
    def debug_connection(self):
        """Debug GitHub connection and configuration"""
        print("=== GitHub Configuration Debug ===")
        print(f"GitHub Token: {'Set' if self.github_token else 'Not Set'}")
        print(f"Repo Owner: {self.repo_owner}")
        print(f"Repo Name: {self.repo_name}")
        print(f"API Base: {self.api_base}")
        
        if not self.github_token:
            print("❌ GitHub token not set, will use local storage")
            return False
        
        try:
            # Test GitHub API connection
            url = f"{self.api_base}"
            response = requests.get(url, headers=self.headers)
            print(f"GitHub API connection test: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ GitHub API connection successful")
                
                # Check data directory
                data_url = f"{self.api_base}/contents/data"
                data_response = requests.get(data_url, headers=self.headers)
                print(f"Data directory check: {data_response.status_code}")
                
                if data_response.status_code == 200:
                    files = data_response.json()
                    print(f"Found {len(files)} files:")
                    for file in files:
                        if file['name'].endswith('.json'):
                            print(f"  - {file['name']}")
                else:
                    print("❌ Data directory does not exist or no access permission")
                    
            else:
                print(f"❌ GitHub API connection failed: {response.status_code}")
                if response.status_code == 401:
                    print("Possible token permission issue")
                elif response.status_code == 404:
                    print("Possible repository does not exist")
                    
        except Exception as e:
            print(f"❌ Connection exception: {e}")
            return False
        
        return True
