#!/usr/bin/env python3
"""Channel-bound YouTube helper. No DELETE requests or generic request CLI."""
import argparse
import json
from pathlib import Path
from urllib import error, parse, request

ROOT = Path(__file__).resolve().parents[2]
ALLOWED = frozenset({('GET', 'channels'), ('GET', 'playlists'), ('GET', 'playlistItems'),
                     ('GET', 'videos'), ('POST', 'playlists'), ('PUT', 'playlists'),
                     ('POST', 'playlistItems'), ('PUT', 'playlistItems')})


def validate_operation(method, resource, params):
    if method != 'GET':
        raise ValueError('Writes disabled: owner selected manual playlist assignment and narrower authorization.')
    if (method, resource) not in ALLOWED:
        raise ValueError('Operation blocked: deletion and unlisted operations are prohibited.')
    if any(str(k).lower() in {'access_token', 'key', 'onbehalfofcontentowner', 'onbehalfofcontentownerchannel'} for k in params):
        raise ValueError('Credential overrides and delegated-channel parameters are prohibited.')


class YouTube:
    def __init__(self):
        self.policy = json.loads((ROOT / 'config/publishing/youtube-policy.json').read_text())
        self.credentials = json.loads((ROOT / 'secrets/youtube-token.json').read_text())
        if self.policy.get('allow_deletion') is not False:
            raise ValueError('Expected explicit no-deletion policy.')
        form = {k: self.credentials[k] for k in ('client_id', 'client_secret', 'refresh_token')}
        form['grant_type'] = 'refresh_token'
        req = request.Request('https://oauth2.googleapis.com/token', data=parse.urlencode(form).encode(), method='POST')
        with request.urlopen(req, timeout=45) as response:
            self.access_token = json.load(response)['access_token']
        channels = self._request('GET', 'channels', {'part': 'snippet', 'mine': 'true'})
        if [c['id'] for c in channels.get('items', [])] != [self.policy['channel_id']]:
            raise ValueError('Connected channel differs from the saved channel; refusing all operations.')

    def _request(self, method, resource, params, body=None):
        validate_operation(method, resource, params)
        url = 'https://www.googleapis.com/youtube/v3/' + resource + '?' + parse.urlencode(params)
        headers = {'Authorization': 'Bearer ' + self.access_token}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers['Content-Type'] = 'application/json'
        req = request.Request(url, data=data, headers=headers, method=method)
        with request.urlopen(req, timeout=45) as response:
            return json.load(response)

    def status(self):
        return {'channel_title': self.policy['channel_title'], 'channel_id': self.policy['channel_id'],
                'deletion_blocked_in_helper': True, 'google_scope_still_permits_deletion': bool(set(self.credentials.get('scopes', [])) & {'https://www.googleapis.com/auth/youtube', 'https://www.googleapis.com/auth/youtube.force-ssl', 'https://www.googleapis.com/auth/youtubepartner'})}

    def playlists(self):
        return self._request('GET', 'playlists', {'part': 'snippet,status', 'mine': 'true', 'maxResults': 50})

    def create_playlist(self, title, description=''):
        return self._request('POST', 'playlists', {'part': 'snippet,status'},
                             {'snippet': {'title': title, 'description': description},
                              'status': {'privacyStatus': 'private'}})

    def _own_playlist(self, playlist_id):
        result = self._request('GET', 'playlists', {'part': 'snippet', 'id': playlist_id})
        items = result.get('items', [])
        if len(items) != 1 or items[0]['snippet']['channelId'] != self.policy['channel_id']:
            raise ValueError('Playlist does not belong to the connected channel.')
        return items[0]

    def update_playlist(self, playlist_id, title, description):
        item = self._own_playlist(playlist_id)
        snippet = {k: v for k, v in item['snippet'].items() if k in ('title', 'description', 'tags', 'defaultLanguage')}
        snippet.update(title=title, description=description)
        return self._request('PUT', 'playlists', {'part': 'snippet'}, {'id': playlist_id, 'snippet': snippet})

    def add_to_playlist(self, playlist_id, video_id, position=None):
        self._own_playlist(playlist_id)
        snippet = {'playlistId': playlist_id, 'resourceId': {'kind': 'youtube#video', 'videoId': video_id}}
        if position is not None:
            snippet['position'] = position
        return self._request('POST', 'playlistItems', {'part': 'snippet'}, {'snippet': snippet})

    def reorder_playlist_item(self, item_id, position):
        data = self._request('GET', 'playlistItems', {'part': 'snippet', 'id': item_id})
        items = data.get('items', [])
        if len(items) != 1:
            raise ValueError('Playlist item not found.')
        snippet = items[0]['snippet']
        self._own_playlist(snippet['playlistId'])
        return self._request('PUT', 'playlistItems', {'part': 'snippet'},
                             {'id': item_id, 'snippet': {'playlistId': snippet['playlistId'],
                              'resourceId': snippet['resourceId'], 'position': position}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('status', 'list-playlists'))
    args = parser.parse_args()
    api = YouTube()
    result = api.status() if args.command == 'status' else api.playlists()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except error.HTTPError as exc:
        raise SystemExit(f'Google request failed (HTTP {exc.code}); provider body and credentials withheld.') from None
    except (OSError, ValueError, KeyError) as exc:
        raise SystemExit(f'YouTube helper stopped ({type(exc).__name__}); credentials withheld.') from None
