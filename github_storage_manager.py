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
        
        # GitHub API 基礎 URL
        self.api_base = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_filename(self, year_month):
        """獲取文件路徑"""
        return f"data/data_{year_month}.json"
    
    def save_data(self, year_month, df):
        """保存數據到 GitHub"""
        if not self.github_token:
            print("GitHub token not found, using local storage")
            return self._save_local_fallback(year_month, df)
        
        try:
            data_dict = df.to_dict('index')
            content = json.dumps(data_dict, ensure_ascii=False, indent=2)
            
            # 編碼為 base64
            content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            file_path = self.get_filename(year_month)
            
            # 檢查文件是否存在
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
        """從 GitHub 加載數據"""
        if not self.github_token:
            return self._load_local_fallback(year_month)
        
        try:
            file_path = self.get_filename(year_month)
            url = f"{self.api_base}/contents/{file_path}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                file_data = response.json()
                content = base64.b64decode(file_data['content']).decode('utf-8')
                data_dict = json.loads(content)
                df = pd.DataFrame.from_dict(data_dict, orient='index')
                return df
            else:
                return None
                
        except Exception as e:
            print(f"Error loading from GitHub: {e}")
            return self._load_local_fallback(year_month)
    
    def data_exists(self, year_month):
        """檢查數據是否存在"""
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
        """獲取所有可用月份"""
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
                        month = file['name'][5:-5]  # 移除 'data_' 和 '.json'
                        months.append(month)
                
                months.sort(reverse=True)
                return months
            else:
                return []
                
        except Exception as e:
            print(f"Error getting months from GitHub: {e}")
            return []
    
    def _get_file_sha(self, file_path):
        """獲取文件的 SHA (用於更新)"""
        try:
            url = f"{self.api_base}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()['sha']
        except:
            pass
        return None
    
    def _save_local_fallback(self, year_month, df):
        """本地存儲回退方案"""
        os.makedirs('dashboard_data', exist_ok=True)
        filename = f"dashboard_data/data_{year_month}.json"
        data_dict = df.to_dict('index')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
        return True
    
    def _load_local_fallback(self, year_month):
        """本地加載回退方案"""
        filename = f"dashboard_data/data_{year_month}.json"
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data_dict = json.load(f)
            return pd.DataFrame.from_dict(data_dict, orient='index')
        return None
    
    # 其他方法保持與原版相同...

    def generate_month_options(self, start_year=2020, end_year=2040):
        """生成月份選項 - 从2020年1月到2040年12月"""
        current_date = datetime.now()
        current_year_month = current_date.strftime("%Y-%m")
        options = []
        
        # 生成从start_year到end_year的所有月份
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                year_month = f"{year}-{month:02d}"
                month_name = f"{year}年{month:02d}月"
                
                # 标记当前月份
                if year_month == current_year_month:
                    label = f"{month_name} (當前)"
                else:
                    label = month_name
                
                options.append({'label': label, 'value': year_month})
    
    # 按时间倒序排列（最新的在前面）
        options.reverse()
    
        return options


    def parse_excel_file(self, contents, filename):
        """解析 Excel 文件 - 移除默认数据填充"""
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            if 'xlsx' in filename or 'xls' in filename:
                df_uploaded = pd.read_excel(io.BytesIO(decoded))
            else:
                return None, "請上傳Excel文件 (.xlsx 或 .xls)"
            
            required_cols = ['Site', 'Monthly Performance', 'Max/Month', 'Completed', 'Missing', 
                            'Week 1', 'Week 2', 'Week 3', 'Week 4']
            
            if not all(col in df_uploaded.columns for col in required_cols):
                missing_cols = [col for col in required_cols if col not in df_uploaded.columns]
                return None, f"缺少必需的列: {', '.join(missing_cols)}"
            
            df_uploaded = df_uploaded.set_index('Site')
            
            # 確保HK_avg存在，如果不存在則添加

            
            # 確保SC_avg存在，如果不存在則添加


            
            return df_uploaded, "文件上傳成功！"
            
        except Exception as e:
            return None, f"解析文件時出錯: {str(e)}"
    
    def delete_month_data(self, year_month):
        """刪除指定年月的數據"""
        if not self.github_token:
            return self._delete_local_fallback(year_month)
        
        try:
            file_path = self.get_filename(year_month)
            sha = self._get_file_sha(file_path)
            
            if not sha:
                return False, f"{year_month} 的數據不存在"
            
            payload = {
                'message': f'Delete 5S data for {year_month}',
                'sha': sha,
                'branch': self.branch
            }
            
            url = f"{self.api_base}/contents/{file_path}"
            response = requests.delete(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                return True, f"已刪除 {year_month} 的GitHub數據"
            else:
                return False, f"刪除GitHub數據失敗: {response.status_code}"
                
        except Exception as e:
            return False, f"刪除數據時出錯: {str(e)}"
    
    def export_month_data(self, year_month):
        """導出指定年月的數據為Excel格式"""
        df = self.load_data(year_month)
        
        if df is None:
            return None, f"{year_month} 的數據不存在"
        
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
            }, "導出成功"
            
        except Exception as e:
            return None, f"導出數據時出錯: {str(e)}"
    
    def _delete_local_fallback(self, year_month):
        """本地刪除回退方案"""
        filename = f"dashboard_data/data_{year_month}.json"
        if os.path.exists(filename):
            try:
                os.remove(filename)
                return True, f"已刪除 {year_month} 的本地數據"
            except Exception as e:
                return False, f"刪除本地數據時出錯: {str(e)}"
        else:
            return False, f"{year_month} 的本地數據不存在"
