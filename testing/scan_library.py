#!/usr/bin/env python3
"""
Utility to scan local directories or Jellyfin for content.
Helps discover files to add to MASTER_SOURCES.
"""

import os
import argparse
import re
import json
import urllib.request
from urllib.error import URLError
import xml.etree.ElementTree as ET

# Common video extensions
VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.m4v', '.mpg', '.ts'}

def clean_filename(filename):
    """Clean up filename to guess a title."""
    name = os.path.splitext(filename)[0]
    # Remove common release group junk
    name = re.sub(r'[\(\[\{].*?[\)\]\}]', '', name)
    name = name.replace('.', ' ').replace('_', ' ')
    return name.strip()

def parse_nfo(nfo_path):
    """Parse .nfo file for metadata."""
    try:
        tree = ET.parse(nfo_path)
        root = tree.getroot()
        
        title = root.findtext('title')
        year = root.findtext('year')
        # Try to find IMDB ID or similar if needed, but title/year is usually enough for queries
        
        # Check root tag to guess type
        if root.tag == 'movie':
            return {'title': title, 'year': year, 'type': 'movie'}
        elif root.tag == 'tvshow':
            return {'title': title, 'year': year, 'type': 'show'}
        elif root.tag == 'episodedetails':
            return {'title': root.findtext('showtitle'), 'type': 'episode'}
    except Exception:
        return None
    return None

def scan_filesystem(path):
    """Recursively scan a directory for video files."""
    if not os.path.exists(path):
        print(f"Error: Path '{path}' not found.")
        return

    print(f"Scanning filesystem: {path}")
    print(f"{'FILENAME':<50} | {'SUGGESTED QUERY'}")
    print("-" * 100)

    count = 0
    for root, _, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                # Check for NFO
                nfo_file = os.path.splitext(file)[0] + ".nfo"
                nfo_path = os.path.join(root, nfo_file)
                
                if os.path.exists(nfo_path):
                    meta = parse_nfo(nfo_path)
                    if meta and meta.get('title'):
                        title = meta['title']
                        if meta['type'] == 'movie':
                            query = f'title:"{title}" AND type:movie'
                            if meta.get('year'):
                                query += f' AND year:{meta["year"]}'
                        elif meta['type'] == 'show' or meta['type'] == 'episode':
                            # For episodes, we usually want the show title
                            query = f'show_title:"{title}"'
                        
                        display_name = (file[:47] + '..') if len(file) > 47 else file
                        print(f"{display_name:<50} | {query}")
                        count += 1
                        continue

                # Try to guess if it's a show or movie
                # Heuristic: S01E01 pattern
                match = re.search(r'[sS](\d+)[eE](\d+)', file)
                
                clean = clean_filename(file)
                
                if match:
                    # Likely a TV Episode
                    # Try to get show name from parent folder if filename is obscure
                    parent_dir = os.path.basename(root)
                    if "Season" in parent_dir:
                        show_name = os.path.basename(os.path.dirname(root))
                    else:
                        show_name = parent_dir
                    
                    # Fallback to filename parsing if folder structure is flat
                    if not show_name or show_name == ".":
                        show_name = file.split(match.group(0))[0].replace('.', ' ').strip()

                    query = f'show_title:"{show_name}"'
                else:
                    # Likely a Movie
                    query = f'title:"{clean}" AND type:movie'

                display_name = (file[:47] + '..') if len(file) > 47 else file
                print(f"{display_name:<50} | {query}")
                count += 1

    print("-" * 100)
    print(f"Found {count} files.")

def scan_jellyfin(url, api_key, user_id=None):
    """Query Jellyfin API for items."""
    # Ensure URL has no trailing slash
    url = url.rstrip('/')
    
    headers = {
        'X-Emby-Token': api_key,
        'Content-Type': 'application/json'
    }

    # 1. Get User ID if not provided
    if not user_id:
        try:
            req = urllib.request.Request(f"{url}/Users", headers=headers)
            with urllib.request.urlopen(req) as response:
                users = json.loads(response.read())
                if users:
                    user_id = users[0]['Id'] # Pick first user
                    print(f"Using User ID: {user_id} ({users[0]['Name']})")
                else:
                    print("Error: No users found in Jellyfin.")
                    return
        except URLError as e:
            print(f"Error connecting to Jellyfin: {e}")
            return

    # 2. Get Items (Recursive)
    # Fields to fetch: Name, ProductionYear, Type
    params = "Recursive=true&IncludeItemTypes=Movie,Series&Fields=Name,ProductionYear,ProviderIds"
    endpoint = f"{url}/Users/{user_id}/Items?{params}"
    
    try:
        req = urllib.request.Request(endpoint, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            
        items = data.get('Items', [])
        
        print(f"Scanning Jellyfin: {url}")
        print(f"{'TITLE':<50} | {'TYPE':<10} | {'SUGGESTED QUERY'}")
        print("-" * 100)
        
        for item in items:
            title = item.get('Name')
            year = item.get('ProductionYear')
            itype = item.get('Type')
            
            if itype == 'Movie':
                query = f'title:"{title}" AND type:movie'
                if year:
                    query += f' AND year:{year}'
            elif itype == 'Series':
                query = f'show_title:"{title}"'
            else:
                continue
                
            display_title = (title[:47] + '..') if len(title) > 47 else title
            print(f"{display_title:<50} | {itype:<10} | {query}")
            
        print("-" * 100)
        print(f"Found {len(items)} items.")

    except URLError as e:
        print(f"Error fetching items from Jellyfin: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan media sources for content.")
    
    subparsers = parser.add_subparsers(dest="command", help="Source to scan")
    
    # Filesystem
    fs_parser = subparsers.add_parser("fs", help="Scan local filesystem")
    fs_parser.add_argument("path", help="Path to directory")
    
    # Jellyfin
    jf_parser = subparsers.add_parser("jellyfin", help="Scan Jellyfin server")
    jf_parser.add_argument("--url", required=True, help="Jellyfin URL (e.g. http://localhost:8096)")
    jf_parser.add_argument("--key", required=True, help="API Key")
    jf_parser.add_argument("--user", help="User ID (optional, defaults to first user)")

    args = parser.parse_args()
    
    if args.command == "fs":
        scan_filesystem(args.path)
    elif args.command == "jellyfin":
        scan_jellyfin(args.url, args.key, args.user)
    else:
        parser.print_help()