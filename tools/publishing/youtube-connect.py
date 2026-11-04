#!/usr/bin/env python3
"""Authorize YouTube through a private loopback callback; Python standard library only."""
import argparse
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import secrets
import time
from urllib import error, parse, request

SCOPE = 'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', type=Path, default=Path(__file__).resolve().parents[2] / 'secrets/youtube-client.json')
    parser.add_argument('--token', type=Path, default=Path(__file__).resolve().parents[2] / 'secrets/youtube-token.json')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if args.token.exists():
        raise SystemExit('Token file already exists; refusing to overwrite it.')
    cfg = json.loads(args.client.read_text()).get('installed', {})
    if not cfg.get('client_id') or not cfg.get('client_secret'):
        raise SystemExit('A Desktop OAuth client JSON is required.')
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    callback = f'http://127.0.0.1:{args.port}/oauth2callback'
    received = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *unused):
            pass  # Callback URLs contain authorization codes; never log them.

        def do_GET(self):
            url = parse.urlsplit(self.path)
            query = parse.parse_qs(url.query)
            valid = url.path == '/oauth2callback' and secrets.compare_digest(query.get('state', [''])[0], state)
            if not valid:
                self.send_error(400, 'Invalid authorization callback')
                return
            if query.get('error'):
                received['denied'] = True
            elif query.get('code'):
                received['code'] = query['code'][0]
            else:
                self.send_error(400, 'Missing authorization code')
                return
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.end_headers()
            self.wfile.write(b'Google authorization response received. Return to the terminal for the connection result.')

    with HTTPServer(('127.0.0.1', args.port), Handler) as server:
        server.timeout = 1
        params = dict(client_id=cfg['client_id'], redirect_uri=callback, response_type='code', scope=SCOPE,
                      state=state, code_challenge=challenge, code_challenge_method='S256',
                      access_type='offline', prompt='consent')
        print('Open this URL in your browser after setting up the SSH tunnel, if using a remote server:', flush=True)
        print('https://accounts.google.com/o/oauth2/v2/auth?' + parse.urlencode(params), flush=True)
        print('Waiting up to 15 minutes. No uploads or playlist changes will be made.', flush=True)
        deadline = time.monotonic() + 900
        while not received and time.monotonic() < deadline:
            server.handle_request()
    if not received or received.get('denied'):
        raise SystemExit('Authorization timed out or was declined. No token saved.')
    form = dict(client_id=cfg['client_id'], client_secret=cfg['client_secret'], code=received['code'],
                redirect_uri=callback, grant_type='authorization_code', code_verifier=verifier)
    req = request.Request('https://oauth2.googleapis.com/token', data=parse.urlencode(form).encode(), method='POST')
    try:
        with request.urlopen(req, timeout=45) as response:
            token = json.load(response)
    except error.HTTPError as exc:
        raise SystemExit(f'Token exchange failed (HTTP {exc.code}); no credentials printed.') from None
    if not token.get('access_token') or not token.get('refresh_token'):
        raise SystemExit('Google did not return both required tokens. No token saved; rerun consent.')
    granted = token.get('scope', '').split()
    if set(granted) != set(SCOPE.split()):
        raise SystemExit('Required YouTube permission was not granted. No token saved.')
    stored = dict(type='authorized_user', client_id=cfg['client_id'], client_secret=cfg['client_secret'],
                  refresh_token=token['refresh_token'], token_uri='https://oauth2.googleapis.com/token', scopes=granted)
    fd = os.open(args.token, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as handle:
        json.dump(stored, handle, indent=2)
        handle.write('\n')
    print(f'Private OAuth token saved: {args.token}', flush=True)
    url = 'https://www.googleapis.com/youtube/v3/channels?' + parse.urlencode(dict(part='snippet', mine='true'))
    req = request.Request(url, headers={'Authorization': 'Bearer ' + token['access_token']})
    try:
        with request.urlopen(req, timeout=45) as response:
            channels = json.load(response)
    except error.HTTPError as exc:
        raise SystemExit(f'Token saved, but channel verification failed (HTTP {exc.code}). Check that YouTube Data API v3 is enabled.') from None
    items = channels.get('items', [])
    if not items:
        raise SystemExit('OAuth succeeded, but Google returned no YouTube channel. Check the selected account.')
    for channel in items:
        print(json.dumps({'connected_channel': channel['snippet']['title'], 'channel_id': channel['id']}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f'Connection setup failed ({type(exc).__name__}); no credentials printed.') from None
    except KeyboardInterrupt:
        raise SystemExit('Authorization cancelled.') from None
