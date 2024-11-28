import requests
import os

class TwitchClipDownloader:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self._get_access_token()
        self.session = requests.Session()
        self.session.headers.update({
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        })

    def _get_access_token(self):
        auth_url = 'https://id.twitch.tv/oauth2/token'
        auth_params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(auth_url, params=auth_params)
        return response.json()['access_token']

    def get_user_id(self, username):
        url = f'https://api.twitch.tv/helix/users?login={username}'
        response = self.session.get(url)
        data = response.json()
        user_id = data['data'][0]['id'] if data['data'] else None
        return user_id

    def get_clips(self, broadcaster_id, creator_id, start_date, end_date, limit=None):
        """
        Récupère les clips pour un broadcaster et un créateur spécifiques.
        """
        url = 'https://api.twitch.tv/helix/clips'
        
        start_datetime = f"{start_date.strftime('%Y-%m-%dT%H:%M:%S')}Z"
        end_datetime = f"{end_date.strftime('%Y-%m-%dT%H:%M:%S')}Z"
        
        # On ne filtre que par broadcaster et dates dans la requête API
        params = {
            'broadcaster_id': broadcaster_id,
            'started_at': start_datetime,
            'ended_at': end_datetime,
            'first': 100
        }
        
        filtered_clips = []
        pagination = None
        
        while True:
            if pagination:
                params['after'] = pagination
            
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                break
            
            data = response.json()
            
            if 'data' in data:
                # Filtrer les clips par creator_id
                new_clips = [clip for clip in data['data'] 
                           if clip['creator_id'] == creator_id]
                filtered_clips.extend(new_clips)
            
            if 'pagination' in data and 'cursor' in data['pagination']:
                pagination = data['pagination']['cursor']
                if limit and len(filtered_clips) >= limit:
                    break
            else:
                break
        
        # Si une limite est spécifiée, on ne retourne que le nombre demandé
        if limit:
            return filtered_clips[:limit]
        
        return filtered_clips

    def get_clip_source_url(self, clip_id):
        gql_url = 'https://gql.twitch.tv/gql'
        headers = {
            'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko'
        }
        
        query = [{
            "operationName": "VideoAccessToken_Clip",
            "variables": {
                "slug": clip_id
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "36b89d2507fce29e5ca551df756d27c1cfe079e2609642b4390aa4c35796eb11"
                }
            }
        }]
        
        try:
            response = requests.post(gql_url, headers=headers, json=query)
            data = response.json()
            
            if response.status_code == 200 and data:
                clip_data = data[0].get('data', {}).get('clip', {})
                if clip_data:
                    playback_url = clip_data.get('playbackAccessToken', {})
                    if playback_url:
                        download_url = clip_data.get('videoQualities', [])[0].get('sourceURL', '')
                        signature = playback_url.get('signature', '')
                        token = playback_url.get('value', '')
                        
                        if download_url and signature and token:
                            final_url = f"{download_url}?sig={signature}&token={token}"
                            return final_url
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de l'URL source: {str(e)}")
            return None

    def download_clip(self, clip, output_dir, progress_callback=None):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        clip_id = clip['id']
        download_url = self.get_clip_source_url(clip_id)
        
        if not download_url:
            return False

        filename = f"{clip['title']}.mp4"
        filename = "".join(c for c in filename if c.isalnum() or c in ['_', '-', '.', ' '])
        filepath = os.path.join(output_dir, filename)

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }

            response = requests.get(download_url, headers=headers, stream=True, timeout=60)
            total_size = int(response.headers.get('content-length', 0))

            if total_size < 100000:
                return False

            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size, filename)

            file_size = os.path.getsize(filepath)
            if file_size < 100000:
                os.remove(filepath)
                return False

            return True

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return False