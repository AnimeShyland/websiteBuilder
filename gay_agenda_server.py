from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify, send_file
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import base64
import io

app = Flask(__name__)
app.secret_key = 'your-super-secret-key-change-this'

# File storage - ensure files are saved in script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(SCRIPT_DIR, 'site_settings.json')
USERS_FILE = os.path.join(SCRIPT_DIR, 'users.json')
MESSAGES_FILE = os.path.join(SCRIPT_DIR, 'messages.json')
SUGGESTIONS_FILE = os.path.join(SCRIPT_DIR, 'suggestions.json')
PROFILES_FILE = os.path.join(SCRIPT_DIR, 'profiles.json')
LAYOUTS_FILE = os.path.join(SCRIPT_DIR, 'layouts.json')
MEDIA_FILE = os.path.join(SCRIPT_DIR, 'media.json')
CUSTOM_ELEMENTS_FILE = os.path.join(SCRIPT_DIR, 'custom_elements.json')

# Default settings with new customization options
DEFAULT_SETTINGS = {
    'site_title': 'The Gay Agenda ♥',
    'fc_name': 'Gay Agenda',
    'server': 'Your Server Name',
    'welcome_message': 'Welcome to our fabulous FFXIV Free Company! ♥',
    'about_text': 'We are a LGBTQ+ friendly Free Company dedicated to having fun, supporting each other, and conquering Eorzea with style and pride! ♥',
    'rainbow_speed': '3s',
    'background_color': '#1a1a2e',
    'text_color': '#ffffff',
    'background_image': '',
    'background_video': '',
    'background_music': '',
    'click_sound': '',
    'music_volume': 0.3,
    'sound_volume': 0.5,
    'layout_mode': 'default',
    'edit_mode': False
}

# Default layout positions
DEFAULT_LAYOUT = {
    'nav_position': {'top': '20px', 'left': '50%', 'transform': 'translateX(-50%)'},
    'content_sections': [
        {'id': 'welcome', 'position': {'top': '120px', 'left': '50px'}, 'size': {'width': '45%', 'height': 'auto'}},
        {'id': 'about', 'position': {'top': '120px', 'right': '50px'}, 'size': {'width': '45%', 'height': 'auto'}},
        {'id': 'join', 'position': {'bottom': '50px', 'left': '50%', 'transform': 'translateX(-50%)'}, 'size': {'width': '90%', 'height': 'auto'}}
    ]
}

# Default admin user
DEFAULT_USERS = {
    'admin': {
        'password_hash': generate_password_hash('admin123'),
        'role': 'admin',
        'created_at': datetime.now().isoformat(),
        'banned': False
    }
}

def load_json_file(filename, default_data):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return default_data.copy() if isinstance(default_data, dict) else default_data[:]
    return default_data.copy() if isinstance(default_data, dict) else default_data[:]

def save_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_settings():
    return load_json_file(SETTINGS_FILE, DEFAULT_SETTINGS)

def save_settings(settings):
    save_json_file(SETTINGS_FILE, settings)

def load_users():
    return load_json_file(USERS_FILE, DEFAULT_USERS)

def save_users(users):
    save_json_file(USERS_FILE, users)

def load_messages():
    return load_json_file(MESSAGES_FILE, [])

def save_messages(messages):
    save_json_file(MESSAGES_FILE, messages)

def load_suggestions():
    return load_json_file(SUGGESTIONS_FILE, [])

def save_suggestions(suggestions):
    save_json_file(SUGGESTIONS_FILE, suggestions)

def load_profiles():
    return load_json_file(PROFILES_FILE, {})

def save_profiles(profiles):
    save_json_file(PROFILES_FILE, profiles)

def load_layouts():
    return load_json_file(LAYOUTS_FILE, DEFAULT_LAYOUT)

def save_layouts(layouts):
    save_json_file(LAYOUTS_FILE, layouts)

def load_media():
    return load_json_file(MEDIA_FILE, {})

def save_media(media):
    save_json_file(MEDIA_FILE, media)

def load_custom_elements():
    return load_json_file(CUSTOM_ELEMENTS_FILE, [])

def save_custom_elements(elements):
    save_json_file(CUSTOM_ELEMENTS_FILE, elements)

def get_user_role():
    return session.get('role', 'guest')

def is_admin():
    return get_user_role() == 'admin'

def is_host_or_admin():
    return get_user_role() in ['host', 'admin']

def is_banned():
    username = session.get('username')
    if not username:
        return False
    users = load_users()
    return users.get(username, {}).get('banned', False)

# Enhanced HTML Template with persistent music and full editing capabilities + FONT CUSTOMIZATION
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ settings.site_title }}</title>
    <!-- Google Fonts for enhanced typography -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700&family=Dancing+Script:wght@400;500;600;700&family=Fredoka+One&family=Righteous&family=Comfortaa:wght@300;400;500;600;700&family=Pacifico&family=Kalam:wght@300;400;700&family=Caveat:wght@400;500;600;700&family=Satisfy&family=Great+Vibes&family=Lobster&family=Orbitron:wght@400;500;600;700;800;900&family=Press+Start+2P&family=Creepster&family=Nosifer&family=Eater&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, {{ settings.background_color }}, #16213e);
            {% if settings.background_image %}
            background-image: url('data:image/jpeg;base64,{{ settings.background_image }}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            {% endif %}
            color: {{ settings.text_color }};
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        
        {% if settings.background_video %}
        #background-video {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: -2;
            opacity: 0.3;
        }
        {% endif %}
        
        /* Font Classes for Custom Typography */
        .font-inter { font-family: 'Inter', sans-serif; }
        .font-poppins { font-family: 'Poppins', sans-serif; }
        .font-dancing { font-family: 'Dancing Script', cursive; }
        .font-fredoka { font-family: 'Fredoka One', cursive; }
        .font-righteous { font-family: 'Righteous', cursive; }
        .font-comfortaa { font-family: 'Comfortaa', cursive; }
        .font-pacifico { font-family: 'Pacifico', cursive; }
        .font-kalam { font-family: 'Kalam', cursive; }
        .font-caveat { font-family: 'Caveat', cursive; }
        .font-satisfy { font-family: 'Satisfy', cursive; }
        .font-great-vibes { font-family: 'Great Vibes', cursive; }
        .font-lobster { font-family: 'Lobster', cursive; }
        .font-orbitron { font-family: 'Orbitron', sans-serif; }
        .font-press-start { font-family: 'Press Start 2P', cursive; }
        .font-creepster { font-family: 'Creepster', cursive; }
        .font-nosifer { font-family: 'Nosifer', cursive; }
        .font-eater { font-family: 'Eater', cursive; }
        
        /* Font Weight Classes */
        .font-light { font-weight: 300; }
        .font-normal { font-weight: 400; }
        .font-medium { font-weight: 500; }
        .font-semibold { font-weight: 600; }
        .font-bold { font-weight: 700; }
        .font-extrabold { font-weight: 800; }
        .font-black { font-weight: 900; }
        
        /* Text Style Classes */
        .text-italic { font-style: italic; }
        .text-underline { text-decoration: underline; }
        .text-line-through { text-decoration: line-through; }
        .text-overline { text-decoration: overline; }
        .text-uppercase { text-transform: uppercase; }
        .text-lowercase { text-transform: lowercase; }
        .text-capitalize { text-transform: capitalize; }
        
        /* Text Size Classes */
        .text-xs { font-size: 0.75rem; }
        .text-sm { font-size: 0.875rem; }
        .text-base { font-size: 1rem; }
        .text-lg { font-size: 1.125rem; }
        .text-xl { font-size: 1.25rem; }
        .text-2xl { font-size: 1.5rem; }
        .text-3xl { font-size: 1.875rem; }
        .text-4xl { font-size: 2.25rem; }
        .text-5xl { font-size: 3rem; }
        .text-6xl { font-size: 3.75rem; }
        
        /* Text Effects */
        .text-shadow { text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
        .text-glow { text-shadow: 0 0 10px #ff69b4, 0 0 20px #ff69b4, 0 0 30px #ff69b4; }
        .text-neon { 
            color: #fff;
            text-shadow: 
                0 0 5px #ff69b4,
                0 0 10px #ff69b4,
                0 0 15px #ff69b4,
                0 0 20px #ff69b4,
                0 0 25px #ff69b4;
        }
        
        /* Letter Spacing */
        .tracking-tight { letter-spacing: -0.025em; }
        .tracking-normal { letter-spacing: 0; }
        .tracking-wide { letter-spacing: 0.025em; }
        .tracking-wider { letter-spacing: 0.05em; }
        .tracking-widest { letter-spacing: 0.1em; }
        
        /* Line Height */
        .leading-tight { line-height: 1.25; }
        .leading-normal { line-height: 1.5; }
        .leading-relaxed { line-height: 1.625; }
        .leading-loose { line-height: 2; }
        
        /* Transparent/Decorative Elements */
        .transparent-element {
            background: none !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            backdrop-filter: none !important;
            box-shadow: none !important;
        }
        
        .transparent-element .fc-info {
            background: none !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Floating hearts animation */
        .heart {
            position: fixed;
            color: #ff69b4;
            font-size: 20px;
            animation: float-heart 6s linear infinite;
            pointer-events: none;
            z-index: 1;
        }
        
        @keyframes float-heart {
            0% {
                transform: translateY(100vh) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) rotate(360deg);
                opacity: 0;
            }
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            {% if settings.get('layout_mode') == 'default' and not settings.get('edit_mode') %}
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            {% endif %}
            position: relative;
            z-index: 2;
        }
        
        .edit-mode .container {
            background: none;
            backdrop-filter: none;
            border: none;
            box-shadow: none;
            padding: 0;
        }
        
        .draggable-element, .editable-element {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.18);
            min-width: 200px;
            min-height: 100px;
            z-index: 10;
            position: relative;
        }
        
        .edit-mode .editable-element {
            border: 2px dashed #ff69b4;
            position: relative;
            cursor: move;
        }
        
        .edit-mode .editable-element:hover {
            border-color: #ff1493;
            background: rgba(255, 105, 180, 0.1);
        }
        
        .edit-mode .editable-element.transforming {
            border: 2px solid #ff1493;
            box-shadow: 0 0 20px rgba(255, 20, 147, 0.5);
        }
        
        /* Transform handles */
        .transform-handles {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            z-index: 1000;
        }
        
        .transform-handle {
            position: absolute;
            background: #ff1493;
            border: 2px solid #fff;
            border-radius: 50%;
            width: 12px;
            height: 12px;
            pointer-events: all;
            cursor: pointer;
        }
        
        /* Corner handles for resizing */
        .handle-nw { top: -6px; left: -6px; cursor: nw-resize; }
        .handle-ne { top: -6px; right: -6px; cursor: ne-resize; }
        .handle-sw { bottom: -6px; left: -6px; cursor: sw-resize; }
        .handle-se { bottom: -6px; right: -6px; cursor: se-resize; }
        
        /* Edge handles for resizing */
        .handle-n { top: -6px; left: 50%; transform: translateX(-50%); cursor: n-resize; }
        .handle-s { bottom: -6px; left: 50%; transform: translateX(-50%); cursor: s-resize; }
        .handle-e { right: -6px; top: 50%; transform: translateY(-50%); cursor: e-resize; }
        .handle-w { left: -6px; top: 50%; transform: translateY(-50%); cursor: w-resize; }
        
        /* Move handle */
        .handle-move {
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            background: #00ff00;
            border-radius: 3px;
            width: 20px;
            height: 16px;
            cursor: move;
        }
        
        /* Rotation handle */
        .handle-rotate {
            top: -40px;
            left: 50%;
            transform: translateX(-50%);
            background: #ffff00;
            border-radius: 3px;
            width: 16px;
            height: 16px;
            cursor: grab;
        }
        
        .handle-rotate:active {
            cursor: grabbing;
        }
        
        /* Transform info display */
        .transform-info {
            position: absolute;
            top: -60px;
            left: 0;
            background: rgba(0, 0, 0, 0.8);
            color: #ff69b4;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            white-space: nowrap;
            pointer-events: none;
        }
        
        /* Grid overlay for snapping */
        .grid-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            z-index: 5;
            opacity: 0.3;
            background-image: 
                linear-gradient(to right, #ff69b4 1px, transparent 1px),
                linear-gradient(to bottom, #ff69b4 1px, transparent 1px);
            background-size: 20px 20px;
            display: none;
        }
        
        .edit-mode.show-grid .grid-overlay {
            display: block;
        }
        
        .element-controls {
            display: none; /* Disabled - using right-click instead */
        }
        
        .rainbow-text {
            background: linear-gradient(45deg, #ff0000, #ff7700, #ffff00, #00ff00, #0000ff, #8b00ff, #ff0000);
            background-size: 600% 600%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: rainbow {{ settings.rainbow_speed }} ease infinite;
            font-weight: bold;
        }
        
        @keyframes rainbow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
        }
        
        .fc-info, .admin-panel, .user-panel, .profile-section {
            background: rgba(255, 255, 255, 0.05);
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            border-left: 5px solid #ff69b4;
        }
        
        .form-group {
            margin: 15px 0;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #ff69b4;
        }
        
        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            font-size: 14px;
        }
        
        .form-group textarea {
            height: 100px;
            resize: vertical;
        }
        
        button {
            background: linear-gradient(45deg, #ff69b4, #ff1493);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            margin: 5px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 105, 180, 0.4);
        }
        
        .btn-danger {
            background: linear-gradient(45deg, #ff4444, #cc0000);
        }
        
        .btn-secondary {
            background: linear-gradient(45deg, #666, #444);
        }
        
        .btn-success {
            background: linear-gradient(45deg, #00ff00, #00cc00);
        }
        
        .login-form, .register-form {
            max-width: 400px;
            margin: 50px auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
        }
        
        .flash-messages {
            margin: 20px 0;
        }
        
        .flash-message {
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            font-weight: bold;
        }
        
        .flash-success {
            background: rgba(0, 255, 0, 0.2);
            border: 1px solid #00ff00;
            color: #00ff00;
        }
        
        .flash-error {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff0000;
            color: #ff0000;
        }
        
        .nav {
            text-align: center;
            margin-bottom: 30px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            position: relative;
        }
        
        .edit-mode .nav {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px;
            border: 2px dashed #ff69b4;
            cursor: move;
            z-index: 100;
        }
        
        .nav a {
            color: #ff69b4;
            text-decoration: none;
            font-weight: bold;
            transition: color 0.3s ease;
            padding: 8px 15px;
            border-radius: 20px;
            background: rgba(255, 105, 180, 0.1);
        }
        
        .nav a:hover {
            color: #ff1493;
            background: rgba(255, 105, 180, 0.2);
        }
        
        .pride-border {
            border: 3px solid;
            border-image: linear-gradient(45deg, #ff0000, #ff7700, #ffff00, #00ff00, #0000ff, #8b00ff) 1;
            border-radius: 10px;
            margin: 20px 0;
            padding: 20px;
        }
        
        .message-channel {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .message {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 3px solid #ff69b4;
        }
        
        .message-header {
            font-weight: bold;
            color: #ff69b4;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .user-badge {
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 10px;
            margin-left: 10px;
        }
        
        .badge-admin { background: #ff1493; color: white; }
        .badge-host { background: #ff69b4; color: white; }
        .badge-guest { background: #666; color: white; }
        
        .user-actions {
            display: none;
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            border-radius: 5px;
            padding: 10px;
            z-index: 1000;
        }
        
        .character-profile {
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 20px;
            margin: 20px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .character-profile:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }
        
        .character-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
            border: 2px solid #ff69b4;
        }
        
        .character-info h3 {
            color: #ff69b4;
            margin-bottom: 10px;
        }
        
        .suggestion-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 3px solid #00ff00;
        }
        
        .users-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .user-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255, 105, 180, 0.3);
        }
        
        .media-controls {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px;
            z-index: 1000;
        }
        
        .profile-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .profile-image {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 10px;
            border: 2px solid #ff69b4;
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        
        .profile-image:hover {
            transform: scale(1.05);
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 10000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
        }
        
        .modal-content {
            position: relative;
            margin: 5% auto;
            padding: 20px;
            width: 90%;
            max-width: 800px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.18);
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .close {
            position: absolute;
            top: 10px;
            right: 20px;
            color: #ff69b4;
            font-size: 30px;
            font-weight: bold;
            cursor: pointer;
        }
        
        /* Edit Mode Toolbar */
        .edit-toolbar {
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.9);
            border-radius: 10px;
            padding: 15px;
            z-index: 10000;
            display: none;
            max-width: 200px;
        }
        
        .edit-mode .edit-toolbar {
            display: block;
        }
        
        .edit-toolbar h3 {
            color: #ff69b4;
            margin-bottom: 15px;
            text-align: center;
            font-size: 16px;
        }
        
        .edit-toolbar button {
            display: block;
            width: 100%;
            margin-bottom: 10px;
            padding: 8px 12px;
            font-size: 14px;
        }
        
        /* Layer System */
        .layer-1 { z-index: 100 !important; }
        .layer-2 { z-index: 200 !important; }
        .layer-3 { z-index: 300 !important; }
        .layer-4 { z-index: 400 !important; }
        .layer-5 { z-index: 500 !important; }
        
        .layer-indicator {
            position: absolute;
            top: -15px;
            right: -15px;
            background: #ff69b4;
            color: white;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            pointer-events: none;
        }
        
        .edit-mode-toggle {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 10001;
            background: rgba(0, 0, 0, 0.9);
            border-radius: 10px;
            padding: 10px;
        }
        
        .screenshot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
        
        .custom-element {
            position: absolute;
            border: 2px dashed transparent;
            padding: 10px;
            min-width: 100px;
            min-height: 50px;
            z-index: 50;
        }
        
        .edit-mode .custom-element {
            border-color: #ff69b4;
            cursor: move;
        }
        
        .element-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 105, 180, 0.1);
            border-radius: 5px;
            display: none;
            pointer-events: none;
        }
        
        .edit-mode .editable-element:hover .element-overlay {
            display: block;
        }
        
        /* Font Customization Modal Styles */
        .font-customization-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }
        
        .font-preview {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border: 2px solid transparent;
        }
        
        .font-preview.active {
            border-color: #ff69b4;
            background: rgba(255, 105, 180, 0.2);
        }
        
        .font-preview:hover {
            background: rgba(255, 255, 255, 0.15);
            cursor: pointer;
        }
        
        @media (max-width: 768px) {
            .character-profile {
                grid-template-columns: 1fr;
            }
            
            .nav {
                flex-direction: column;
            }
            
            .edit-mode .editable-element {
                position: relative !important;
                margin: 10px 0;
            }
            
            .edit-toolbar {
                position: relative;
                top: auto;
                left: auto;
                margin-bottom: 20px;
            }
            
            .font-customization-panel {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body class="{{ 'edit-mode' if settings.get('edit_mode') else '' }}">
    {% if settings.background_video %}
    <video id="background-video" autoplay muted loop>
        <source src="data:video/mp4;base64,{{ settings.background_video }}" type="video/mp4">
    </video>
    {% endif %}

    <!-- Edit Mode Toggle (Admin Only) -->
    {% if session.get('role') == 'admin' %}
    <div class="edit-mode-toggle">
        <button onclick="toggleEditMode()" class="{{ 'btn-danger' if settings.get('edit_mode') else 'btn-success' }}">
            {{ 'Exit Edit Mode' if settings.get('edit_mode') else 'Enter Edit Mode' }}
        </button>
    </div>
    {% endif %}

    <!-- Edit Toolbar (Edit Mode Only) -->
    <div class="edit-toolbar">
        <h3>Design Studio ♥</h3>
        <button onclick="addTextElement()">✏️ Add Text</button>
        <button onclick="addImageElement()">🖼️ Add Image</button>
        <button onclick="addVideoElement()">🎬 Add Video/GIF</button>
        <button onclick="addLabelElement()">🏷️ Add Label</button>
        <button onclick="addDiscordElement()">💬 Add Discord</button>
        <hr style="margin: 10px 0; border-color: #ff69b4;">
        <button onclick="openLayerManager()" class="btn-secondary">📚 Layer Manager</button>
        <button onclick="openElementManager()" class="btn-secondary">🗂️ All Elements</button>
        <hr style="margin: 10px 0; border-color: #ff69b4;">
        <button onclick="toggleGrid()" class="btn-secondary" id="gridToggle">Show Grid</button>
        <button onclick="resetAllTransforms()" class="btn-danger">Reset Positions</button>
        <hr style="margin: 10px 0; border-color: #ff69b4;">
        <button onclick="previewMode()" class="btn-secondary">Preview (5s)</button>
        <small style="color: #ff69b4; display: block; margin-top: 10px; text-align: center; font-size: 11px;">
            ✨ Click elements to transform!<br>
            🎯 Right-click: Edit/Delete/Copy/Layers<br>
            🎨 Transparent Mode for overlays<br>
            ⌨️ Ctrl+G: Grid, Del: Delete, Esc: Deselect<br>
            📚 5-Layer System: Front to Back<br>
            🎭 Advanced Font Customization!
        </small>
    </div>

    <div class="container">
        <!-- Grid overlay for design precision -->
        <div class="grid-overlay"></div>
        
        <div class="nav {{ 'editable-element' if settings.get('edit_mode') else '' }}" id="navigation" data-type="navigation">
            {% if settings.get('edit_mode') %}
            <div class="element-overlay"></div>
            {% endif %}
            <a href="/" onclick="playClickSound()">Home</a>
            <a href="/characters" onclick="playClickSound()">Characters</a>
            <a href="/messages" onclick="playClickSound()">Messages</a>
            {% if session.get('username') %}
                <a href="/suggestions" onclick="playClickSound()">Suggestions</a>
                {% if session.get('role') in ['host', 'admin'] %}
                    <a href="/profile" onclick="playClickSound()">My Profile</a>
                {% endif %}
                {% if session.get('role') == 'admin' %}
                    <a href="/admin" onclick="playClickSound()">🎨 Admin Panel</a>
                    <a href="/manage-users" onclick="playClickSound()">👥 Manage Users</a>
                {% endif %}
                <a href="/logout" onclick="playClickSound()">Logout ({{ session.username }} - {{ session.get('role', 'unknown') }})</a>
            {% else %}
                <a href="/login" onclick="playClickSound()">Login</a>
                <a href="/register" onclick="playClickSound()">Register</a>
            {% endif %}
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash-message flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        {{ content | safe }}
    </div>
    
    <!-- Render custom elements -->
    {% for element in custom_elements %}
    <div class="custom-element {{ 'editable-element' if settings.get('edit_mode') else '' }}" 
         id="custom-{{ element.id }}" 
         style="top: {{ element.position.get('top', '150px') }}; left: {{ element.position.get('left', '50px') }}; 
                width: {{ element.size.get('width', '300px') }}; height: {{ element.size.get('height', 'auto') }};"
         data-type="{{ element.type }}" data-id="{{ element.id }}">
        {% if settings.get('edit_mode') %}
        <div class="element-overlay"></div>
        <div class="element-controls">
            <button onclick="editElement('custom-{{ element.id }}')">Edit</button>
            <button onclick="deleteElement('custom-{{ element.id }}')">Delete</button>
        </div>
        {% endif %}
        {% if element.type == 'text' %}
            <div>{{ element.content | safe }}</div>
        {% elif element.type == 'image' %}
            <img src="{{ element.content }}" style="width: 100%; height: auto;" alt="Custom Image">
        {% elif element.type == 'video' %}
            <video {{ 'controls' if element.get('controls', True) else '' }} style="width: 100%; height: auto;">
                <source src="{{ element.content }}" type="video/mp4">
            </video>
        {% elif element.type == 'label' %}
            <label style="color: #ff69b4; font-weight: bold; {{ element.get('style', '') }}">{{ element.content }}</label>
        {% else %}
            {{ element.content | safe }}
        {% endif %}
    </div>
    {% endfor %}
    
    <!-- Persistent Audio Elements -->
    {% if settings.background_music %}
    <audio id="persistent-music" loop>
        <source src="data:audio/mpeg;base64,{{ settings.background_music }}" type="audio/mpeg">
    </audio>
    {% endif %}
    
    {% if settings.click_sound %}
    <audio id="click-sound" preload="auto">
        <source src="data:audio/mpeg;base64,{{ settings.click_sound }}" type="audio/mpeg">
    </audio>
    {% endif %}
    
    {% if settings.background_music or settings.click_sound %}
    <div class="media-controls">
        {% if settings.background_music %}
        <div>
            <label>Music: </label>
            <button onclick="toggleMusic()" id="music-toggle">⏯️</button>
            <input type="range" id="music-volume" min="0" max="1" step="0.1" value="{{ settings.music_volume }}" onchange="setMusicVolume(this.value)">
        </div>
        {% endif %}
        {% if settings.click_sound %}
        <div>
            <label>Sound FX: </label>
            <input type="range" id="sound-volume" min="0" max="1" step="0.1" value="{{ settings.sound_volume }}" onchange="setSoundVolume(this.value)">
        </div>
        {% endif %}
    </div>
    {% endif %}
    
    <!-- Element Creation Modal -->
    <div id="elementModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('elementModal')">&times;</span>
            <h3 class="rainbow-text">Add New Element ♥</h3>
            <div id="elementForm">
                <!-- Dynamic form content -->
            </div>
        </div>
    </div>
    
    <!-- Font Customization Modal -->
    <div id="fontModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('fontModal')">&times;</span>
            <h3 class="rainbow-text">Font Customization Studio ♥</h3>
            <div id="fontCustomization">
                <!-- Font customization content -->
            </div>
        </div>
    </div>
    
    <!-- Layer Manager Modal -->
    <div id="layerModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('layerModal')">&times;</span>
            <h3 class="rainbow-text">Layer Manager ♥</h3>
            <div id="layerManager">
                <p style="color: #ff69b4; margin-bottom: 15px;">Manage element layers (5 = Front, 1 = Back)</p>
                <div id="layerList"></div>
            </div>
        </div>
    </div>
    
    <!-- Element Manager Modal -->
    <div id="elementModal2" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('elementModal2')">&times;</span>
            <h3 class="rainbow-text">All Site Elements ♥</h3>
            <div id="elementManager">
                <p style="color: #ff69b4; margin-bottom: 15px;">Manage elements across all pages</p>
                <div id="elementsList"></div>
            </div>
        </div>
    </div>
    
    <!-- Element Edit Modal -->
    <div id="editElementModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('editElementModal')">&times;</span>
            <h3 class="rainbow-text">Edit Element ♥</h3>
            <div id="editElementForm">
                <!-- Dynamic edit form content -->
            </div>
        </div>
    </div>
    
    <script>
        // Available fonts database
        const FONT_OPTIONS = [
            {
                name: 'Inter (Modern Sans)',
                class: 'font-inter',
                preview: 'Clean and modern typography',
                category: 'sans-serif'
            },
            {
                name: 'Poppins (Friendly Sans)',
                class: 'font-poppins',
                preview: 'Friendly and approachable design',
                category: 'sans-serif'
            },
            {
                name: 'Dancing Script (Handwritten)',
                class: 'font-dancing',
                preview: 'Elegant handwritten style',
                category: 'cursive'
            },
            {
                name: 'Fredoka One (Fun & Bold)',
                class: 'font-fredoka',
                preview: 'Fun and playful headlines',
                category: 'display'
            },
            {
                name: 'Righteous (Strong Display)',
                class: 'font-righteous',
                preview: 'Strong and confident display',
                category: 'display'
            },
            {
                name: 'Comfortaa (Rounded)',
                class: 'font-comfortaa',
                preview: 'Soft and comfortable reading',
                category: 'rounded'
            },
            {
                name: 'Pacifico (Brush Script)',
                class: 'font-pacifico',
                preview: 'Casual brush lettering style',
                category: 'script'
            },
            {
                name: 'Kalam (Handwritten)',
                class: 'font-kalam',
                preview: 'Natural handwriting feel',
                category: 'handwriting'
            },
            {
                name: 'Caveat (Marker Pen)',
                class: 'font-caveat',
                preview: 'Marker pen handwriting',
                category: 'handwriting'
            },
            {
                name: 'Satisfy (Casual Script)',
                class: 'font-satisfy',
                preview: 'Relaxed script lettering',
                category: 'script'
            },
            {
                name: 'Great Vibes (Formal Script)',
                class: 'font-great-vibes',
                preview: 'Elegant formal script',
                category: 'script'
            },
            {
                name: 'Lobster (Retro Script)',
                class: 'font-lobster',
                preview: 'Retro script with character',
                category: 'script'
            },
            {
                name: 'Orbitron (Futuristic)',
                class: 'font-orbitron',
                preview: 'Futuristic sci-fi styling',
                category: 'futuristic'
            },
            {
                name: 'Press Start 2P (Pixel)',
                class: 'font-press-start',
                preview: 'Retro 8-bit gaming style',
                category: 'gaming'
            },
            {
                name: 'Creepster (Horror)',
                class: 'font-creepster',
                preview: 'Spooky horror movie style',
                category: 'horror'
            },
            {
                name: 'Nosifer (Gothic Horror)',
                class: 'font-nosifer',
                preview: 'Gothic vampire aesthetic',
                category: 'horror'
            },
            {
                name: 'Eater (Bloody Horror)',
                class: 'font-eater',
                preview: 'Dripping blood effect',
                category: 'horror'
            }
        ];
        
        const FONT_WEIGHTS = [
            { name: 'Light', class: 'font-light', weight: '300' },
            { name: 'Normal', class: 'font-normal', weight: '400' },
            { name: 'Medium', class: 'font-medium', weight: '500' },
            { name: 'Semi Bold', class: 'font-semibold', weight: '600' },
            { name: 'Bold', class: 'font-bold', weight: '700' },
            { name: 'Extra Bold', class: 'font-extrabold', weight: '800' },
            { name: 'Black', class: 'font-black', weight: '900' }
        ];
        
        const FONT_SIZES = [
            { name: 'Extra Small', class: 'text-xs', size: '12px' },
            { name: 'Small', class: 'text-sm', size: '14px' },
            { name: 'Base', class: 'text-base', size: '16px' },
            { name: 'Large', class: 'text-lg', size: '18px' },
            { name: 'Extra Large', class: 'text-xl', size: '20px' },
            { name: '2X Large', class: 'text-2xl', size: '24px' },
            { name: '3X Large', class: 'text-3xl', size: '30px' },
            { name: '4X Large', class: 'text-4xl', size: '36px' },
            { name: '5X Large', class: 'text-5xl', size: '48px' },
            { name: '6X Large', class: 'text-6xl', size: '60px' }
        ];
        
        const TEXT_EFFECTS = [
            { name: 'Normal', class: '', description: 'Standard text' },
            { name: 'Italic', class: 'text-italic', description: 'Slanted text' },
            { name: 'Underline', class: 'text-underline', description: 'Underlined text' },
            { name: 'Line Through', class: 'text-line-through', description: 'Crossed out text' },
            { name: 'Overline', class: 'text-overline', description: 'Line above text' },
            { name: 'Uppercase', class: 'text-uppercase', description: 'ALL CAPS' },
            { name: 'Lowercase', class: 'text-lowercase', description: 'all lowercase' },
            { name: 'Capitalize', class: 'text-capitalize', description: 'Title Case' },
            { name: 'Shadow', class: 'text-shadow', description: 'Drop shadow effect' },
            { name: 'Glow', class: 'text-glow', description: 'Pink glow effect' },
            { name: 'Neon', class: 'text-neon', description: 'Bright neon glow' },
            { name: 'Rainbow', class: 'rainbow-text', description: 'Animated rainbow colors' }
        ];
        
        const LETTER_SPACING = [
            { name: 'Tight', class: 'tracking-tight', spacing: '-0.025em' },
            { name: 'Normal', class: 'tracking-normal', spacing: '0' },
            { name: 'Wide', class: 'tracking-wide', spacing: '0.025em' },
            { name: 'Wider', class: 'tracking-wider', spacing: '0.05em' },
            { name: 'Widest', class: 'tracking-widest', spacing: '0.1em' }
        ];
        
        const LINE_HEIGHT = [
            { name: 'Tight', class: 'leading-tight', height: '1.25' },
            { name: 'Normal', class: 'leading-normal', height: '1.5' },
            { name: 'Relaxed', class: 'leading-relaxed', height: '1.625' },
            { name: 'Loose', class: 'leading-loose', height: '2' }
        ];
        
        // Global font customization state
        let currentFontCustomization = {
            font: 'font-inter',
            weight: 'font-normal',
            size: 'text-base',
            effects: [],
            spacing: 'tracking-normal',
            lineHeight: 'leading-normal'
        };
        
        // Persistent Music Management
        let musicState = {
            isPlaying: false,
            currentTime: 0,
            volume: {{ settings.music_volume }}
        };
        
        // Load music state from localStorage
        function loadMusicState() {
            const saved = localStorage.getItem('gayAgendaMusicState');
            if (saved) {
                musicState = JSON.parse(saved);
            }
        }
        
        // Save music state to localStorage
        function saveMusicState() {
            localStorage.setItem('gayAgendaMusicState', JSON.stringify(musicState));
        }
        
        // Initialize persistent music
        function initPersistentMusic() {
            const music = document.getElementById('persistent-music');
            if (music) {
                loadMusicState();
                music.volume = musicState.volume;
                
                // Set current time if valid
                if (musicState.currentTime && !isNaN(musicState.currentTime)) {
                    music.currentTime = musicState.currentTime;
                }
                
                // Aggressive autoplay - try multiple methods to resume music
                if (musicState.isPlaying) {
                    attemptMusicResume(music);
                }
                
                // Save state periodically
                setInterval(() => {
                    if (music && !music.paused) {
                        musicState.currentTime = music.currentTime;
                        musicState.isPlaying = true;
                        saveMusicState();
                    }
                }, 1000);
                
                // Handle music events
                music.addEventListener('play', () => {
                    musicState.isPlaying = true;
                    saveMusicState();
                    updateMusicButton();
                });
                
                music.addEventListener('pause', () => {
                    musicState.isPlaying = false;
                    musicState.currentTime = music.currentTime;
                    saveMusicState();
                    updateMusicButton();
                });
                
                // Update button state
                updateMusicButton();
            }
        }
        
        // Try multiple methods to resume music playback
        function attemptMusicResume(music) {
            let attempts = 0;
            const maxAttempts = 5;
            
            function tryPlay() {
                if (attempts >= maxAttempts) {
                    console.log('Music autoplay failed after multiple attempts - user interaction required');
                    return;
                }
                
                attempts++;
                music.currentTime = musicState.currentTime || 0;
                
                const playPromise = music.play();
                if (playPromise !== undefined) {
                    playPromise.then(() => {
                        console.log('Music resumed successfully!');
                        musicState.isPlaying = true;
                        saveMusicState();
                        updateMusicButton();
                    }).catch((error) => {
                        console.log(`Music autoplay attempt ${attempts} failed:`, error);
                        setTimeout(tryPlay, 500);
                    });
                }
            }
            
            tryPlay();
            
            const enableMusicOnInteraction = () => {
                if (musicState.isPlaying && music.paused) {
                    music.currentTime = musicState.currentTime || 0;
                    music.play().then(() => {
                        console.log('Music resumed after user interaction');
                        updateMusicButton();
                    }).catch(e => console.log('Music resume on interaction failed:', e));
                }
                document.removeEventListener('click', enableMusicOnInteraction);
                document.removeEventListener('keydown', enableMusicOnInteraction);
                document.removeEventListener('touchstart', enableMusicOnInteraction);
            };
            
            document.addEventListener('click', enableMusicOnInteraction);
            document.addEventListener('keydown', enableMusicOnInteraction);
            document.addEventListener('touchstart', enableMusicOnInteraction);
        }
        
        function toggleMusic() {
            const music = document.getElementById('persistent-music');
            if (music) {
                if (music.paused) {
                    music.currentTime = musicState.currentTime || 0;
                    music.play().then(() => {
                        console.log('Music resumed from position:', music.currentTime);
                        musicState.isPlaying = true;
                        saveMusicState();
                        updateMusicButton();
                    }).catch(e => {
                        console.log('Music play failed:', e);
                        alert('Music playback failed. Please try again.');
                    });
                } else {
                    musicState.currentTime = music.currentTime;
                    music.pause();
                    musicState.isPlaying = false;
                    saveMusicState();
                    updateMusicButton();
                    console.log('Music paused at position:', musicState.currentTime);
                }
            }
        }
        
        function updateMusicButton() {
            const button = document.getElementById('music-toggle');
            const music = document.getElementById('persistent-music');
            if (button && music) {
                button.innerHTML = music.paused ? '▶️' : '⏸️';
            }
        }
        
        function setMusicVolume(volume) {
            const music = document.getElementById('persistent-music');
            if (music) {
                music.volume = volume;
                musicState.volume = volume;
                saveMusicState();
            }
        }
        
        function setSoundVolume(volume) {
            const sound = document.getElementById('click-sound');
            if (sound) {
                sound.volume = volume;
                localStorage.setItem('gayAgendaSoundVolume', volume);
            }
        }
        
        function playClickSound() {
            const sound = document.getElementById('click-sound');
            if (sound) {
                sound.currentTime = 0;
                sound.play().catch(e => console.log('Sound play failed:', e));
            }
        }
        
        // Edit Mode Functions - Work with current page context
        let currentPage = window.location.pathname;
        
        function toggleEditMode() {
            fetch('/toggle-edit-mode', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            }).then(() => location.reload());
        }
        
        function editElement(elementId) {
            // Edit existing site elements, not custom ones
            switch(elementId) {
                case 'welcome':
                    editContentSection('welcome_message', 'Welcome Message');
                    break;
                case 'about':
                    editContentSection('about_text', 'About Text');
                    break;
                case 'navigation':
                    alert('Navigation editing - modify links in Admin Panel');
                    break;
                default:
                    if (elementId.startsWith('custom-')) {
                        showDeleteContextMenu(elementId);
                    } else {
                        alert('Element editing coming soon!');
                    }
            }
        }
        
        function editContentSection(settingKey, displayName) {
            const currentValue = getCurrentSettingValue(settingKey);
            const newValue = prompt(`Edit ${displayName}:`, currentValue);
            
            if (newValue !== null && newValue !== currentValue) {
                updateSiteSetting(settingKey, newValue);
            }
        }
        
        function getCurrentSettingValue(key) {
            // Extract current values from the page
            switch(key) {
                case 'welcome_message':
                    const welcomeEl = document.querySelector('#welcome p');
                    return welcomeEl ? welcomeEl.textContent : 'Welcome to our fabulous FFXIV Free Company! ♥';
                case 'about_text':
                    const aboutEl = document.querySelector('#about p');
                    return aboutEl ? aboutEl.textContent : 'We are a LGBTQ+ friendly Free Company...';
                default:
                    return '';
            }
        }
        
        function updateSiteSetting(key, value) {
            fetch('/update-site-content', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: key, value: value})
            }).then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Content updated! ♥');
                    location.reload();
                } else {
                    alert('Error updating content: ' + (data.error || 'Unknown error'));
                }
            }).catch(error => {
                console.error('Error:', error);
                alert('Error updating content!');
            });
        }
        
        function addTextElement() {
            openElementModal('text');
        }
        
        function addImageElement() {
            openElementModal('image');
        }
        
        function addVideoElement() {
            openElementModal('video');
        }
        
        function addLabelElement() {
            openElementModal('label');
        }
        
        function addDiscordElement() {
            openElementModal('discord');
        }
        
        function getPageSpecificSections() {
            // Return sections based on current page
            const path = window.location.pathname;
            
            switch(path) {
                case '/':
                    return [
                        {value: 'new', text: 'Create New Section'},
                        {value: 'welcome', text: 'Add to Welcome Section'},
                        {value: 'about', text: 'Add to About Section'},
                        {value: 'join', text: 'Add to Mare Section'}
                    ];
                case '/characters':
                    return [
                        {value: 'new', text: 'Create New Section'},
                        {value: 'characters-panel', text: 'Add to Characters Section'}
                    ];
                case '/messages':
                    return [
                        {value: 'new', text: 'Create New Section'},
                        {value: 'messages-panel', text: 'Add to Messages Section'}
                    ];
                case '/suggestions':
                    return [
                        {value: 'new', text: 'Create New Section'},
                        {value: 'suggestions-panel', text: 'Add to Suggestions Section'}
                    ];
                case '/profile':
                    return [
                        {value: 'new', text: 'Create New Section'},
                        {value: 'profile-panel', text: 'Add to Profile Section'}
                    ];
                case '/admin':
                    return [
                        {value: 'new', text: 'Create New Section'},
                        {value: 'admin-panel', text: 'Add to Admin Section'}
                    ];
                case '/manage-users':
                    return [
                        {value: 'new', text: 'Create New Section'},
                        {value: 'manage-users-panel', text: 'Add to User Management Section'}
                    ];
                default:
                    return [
                        {value: 'new', text: 'Create New Section'},
                        {value: 'main-content', text: 'Add to Main Content'}
                    ];
            }
        }
        
        function openElementModal(type) {
            const modal = document.getElementById('elementModal');
            const form = document.getElementById('elementForm');
            const sections = getPageSpecificSections();
            
            // Build section options
            let sectionOptions = '';
            sections.forEach(section => {
                sectionOptions += `<option value="${section.value}">${section.text}</option>`;
            });
            
            let formContent = '';
            switch(type) {
                case 'text':
                    formContent = `
                        <div class="form-group">
                            <label>Text Content:</label>
                            <textarea id="elementContent" placeholder="Enter your text here..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>Add to Section:</label>
                            <select id="targetSection">
                                ${sectionOptions}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Text Style:</label>
                            <select id="textStyle">
                                <option value="normal">Normal</option>
                                <option value="rainbow">Rainbow</option>
                                <option value="header">Header</option>
                                <option value="subtitle">Subtitle</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <button type="button" onclick="openFontCustomizer()" class="btn-secondary" style="width: 100%;">
                                🎨 Advanced Font Customization
                            </button>
                            <small style="color: #ff69b4; display: block; margin-top: 5px;">
                                Choose fonts, weights, sizes, effects, and more!
                            </small>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="transparentMode"> 
                                Transparent/Decorative Mode (no background styling)
                            </label>
                        </div>
                        <button onclick="addTextToSite()">Add Text ♥</button>
                    `;
                    break;
                case 'image':
                    formContent = `
                        <div class="form-group">
                            <label>Image Upload:</label>
                            <input type="file" id="imageFile" accept="image/*">
                        </div>
                        <div class="form-group">
                            <label>Add to Section:</label>
                            <select id="targetSection">
                                ${sectionOptions}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Caption:</label>
                            <input type="text" id="imageCaption" placeholder="Image description...">
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="transparentMode"> 
                                Transparent/Decorative Mode (no background, perfect for overlays)
                            </label>
                        </div>
                        <button onclick="addImageToSite()">Add Image ♥</button>
                    `;
                    break;
                case 'video':
                    formContent = `
                        <div class="form-group">
                            <label>Video/GIF Upload:</label>
                            <input type="file" id="videoFile" accept="video/*,image/gif">
                        </div>
                        <div class="form-group">
                            <label>Add to Section:</label>
                            <select id="targetSection">
                                ${sectionOptions}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="videoControls" checked> 
                                Show Video Controls (uncheck for GIFs/decorative videos)
                            </label>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="transparentMode"> 
                                Transparent/Decorative Mode (perfect for animated overlays)
                            </label>
                        </div>
                        <button onclick="addVideoToSite()">Add Video/GIF ♥</button>
                    `;
                    break;
                case 'label':
                    formContent = `
                        <div class="form-group">
                            <label>Label Text:</label>
                            <input type="text" id="labelText" placeholder="Enter label text">
                        </div>
                        <div class="form-group">
                            <label>Add to Section:</label>
                            <select id="targetSection">
                                ${sectionOptions}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Label Style:</label>
                            <select id="labelStyle">
                                <option value="normal">Normal</option>
                                <option value="rainbow">Rainbow</option>
                                <option value="bold">Bold</option>
                                <option value="italic">Italic</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <button type="button" onclick="openFontCustomizer()" class="btn-secondary" style="width: 100%;">
                                🎨 Advanced Font Customization
                            </button>
                            <small style="color: #ff69b4; display: block; margin-top: 5px;">
                                Choose fonts, weights, sizes, effects, and more!
                            </small>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="transparentMode"> 
                                Transparent/Decorative Mode (no background styling)
                            </label>
                        </div>
                        <button onclick="addLabelToSite()">Add Label ♥</button>
                    `;
                    break;
                case 'discord':
                    formContent = `
                        <div class="form-group">
                            <label>Discord Embed URL:</label>
                            <input type="url" id="discordUrl" placeholder="https://discord.com/widget?id=YOUR_SERVER_ID&theme=dark">
                            <small style="color: #ff69b4; display: block; margin-top: 5px;">
                                Get this from Discord Server Settings → Widget → Widget URL
                            </small>
                        </div>
                        <div class="form-group">
                            <label>Add to Section:</label>
                            <select id="targetSection">
                                ${sectionOptions}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Title:</label>
                            <input type="text" id="discordTitle" value="Discord Server" placeholder="Discord Announcements">
                        </div>
                        <div class="form-group">
                            <label>Height:</label>
                            <select id="discordHeight">
                                <option value="300px">Small (300px)</option>
                                <option value="400px" selected>Medium (400px)</option>
                                <option value="500px">Large (500px)</option>
                                <option value="600px">Extra Large (600px)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="transparentMode"> 
                                Transparent Mode (no Discord styling, blend with page)
                            </label>
                        </div>
                        <button onclick="addDiscordToSite()">Add Discord Embed ♥</button>
                    `;
                    break;
            }
            
            form.innerHTML = formContent;
            modal.style.display = 'block';
        }
        
        function openFontCustomizer() {
            const modal = document.getElementById('fontModal');
            const customization = document.getElementById('fontCustomization');
            
            customization.innerHTML = `
                <div class="font-customization-panel">
                    <div>
                        <h4 style="color: #ff69b4; margin-bottom: 15px;">🎨 Font Family</h4>
                        <div id="fontFamilyOptions" style="max-height: 300px; overflow-y: auto;">
                            ${FONT_OPTIONS.map(font => `
                                <div class="font-preview ${font.class}" onclick="selectFont('${font.class}')" data-font="${font.class}">
                                    <strong>${font.name}</strong><br>
                                    <small>${font.preview}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div>
                        <h4 style="color: #ff69b4; margin-bottom: 15px;">⚖️ Font Weight</h4>
                        <div id="fontWeightOptions">
                            ${FONT_WEIGHTS.map(weight => `
                                <div class="font-preview ${weight.class}" onclick="selectWeight('${weight.class}')" data-weight="${weight.class}">
                                    <span style="font-weight: ${weight.weight};">${weight.name}</span>
                                </div>
                            `).join('')}
                        </div>
                        
                        <h4 style="color: #ff69b4; margin: 15px 0;">📏 Font Size</h4>
                        <div id="fontSizeOptions">
                            ${FONT_SIZES.map(size => `
                                <div class="font-preview ${size.class}" onclick="selectSize('${size.class}')" data-size="${size.class}">
                                    <span style="font-size: ${size.size};">${size.name}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="font-customization-panel">
                    <div>
                        <h4 style="color: #ff69b4; margin-bottom: 15px;">✨ Text Effects</h4>
                        <div id="textEffectsOptions">
                            ${TEXT_EFFECTS.map(effect => `
                                <div class="font-preview ${effect.class}" onclick="toggleEffect('${effect.class}')" data-effect="${effect.class}">
                                    <span class="${effect.class}">${effect.name}</span><br>
                                    <small>${effect.description}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div>
                        <h4 style="color: #ff69b4; margin-bottom: 15px;">📐 Spacing & Layout</h4>
                        <div id="spacingOptions">
                            <p style="color: #ff69b4; margin: 10px 0;"><strong>Letter Spacing:</strong></p>
                            ${LETTER_SPACING.map(spacing => `
                                <div class="font-preview ${spacing.class}" onclick="selectSpacing('${spacing.class}')" data-spacing="${spacing.class}">
                                    <span class="${spacing.class}">${spacing.name}</span>
                                </div>
                            `).join('')}
                            
                            <p style="color: #ff69b4; margin: 15px 0 10px 0;"><strong>Line Height:</strong></p>
                            ${LINE_HEIGHT.map(height => `
                                <div class="font-preview ${height.class}" onclick="selectLineHeight('${height.class}')" data-line-height="${height.class}">
                                    <span class="${height.class}">${height.name}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div style="margin: 20px 0; padding: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 10px;">
                    <h4 style="color: #ff69b4; margin-bottom: 15px;">👀 Live Preview</h4>
                    <div id="fontPreview" style="font-size: 18px; padding: 15px; background: rgba(0, 0, 0, 0.3); border-radius: 5px;">
                        This is your custom text with all the styling applied! ♥
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <button onclick="applyFontCustomization()" class="btn-success">Apply Font Settings ♥</button>
                    <button onclick="resetFontCustomization()" class="btn-secondary">Reset to Default</button>
                    <button onclick="closeModal('fontModal')" class="btn-danger">Cancel</button>
                </div>
            `;
            
            updateFontPreview();
            updateActiveSelections();
            modal.style.display = 'block';
        }
        
        function selectFont(fontClass) {
            currentFontCustomization.font = fontClass;
            updateFontPreview();
            updateActiveSelections();
        }
        
        function selectWeight(weightClass) {
            currentFontCustomization.weight = weightClass;
            updateFontPreview();
            updateActiveSelections();
        }
        
        function selectSize(sizeClass) {
            currentFontCustomization.size = sizeClass;
            updateFontPreview();
            updateActiveSelections();
        }
        
        function toggleEffect(effectClass) {
            if (effectClass === '') return;
            
            const index = currentFontCustomization.effects.indexOf(effectClass);
            if (index > -1) {
                currentFontCustomization.effects.splice(index, 1);
            } else {
                currentFontCustomization.effects.push(effectClass);
            }
            
            updateFontPreview();
            updateActiveSelections();
        }
        
        function selectSpacing(spacingClass) {
            currentFontCustomization.spacing = spacingClass;
            updateFontPreview();
            updateActiveSelections();
        }
        
        function selectLineHeight(lineHeightClass) {
            currentFontCustomization.lineHeight = lineHeightClass;
            updateFontPreview();
            updateActiveSelections();
        }
        
        function updateFontPreview() {
            const preview = document.getElementById('fontPreview');
            if (preview) {
                const allClasses = [
                    currentFontCustomization.font,
                    currentFontCustomization.weight,
                    currentFontCustomization.size,
                    currentFontCustomization.spacing,
                    currentFontCustomization.lineHeight,
                    ...currentFontCustomization.effects
                ].join(' ');
                
                preview.className = allClasses;
            }
        }
        
        function updateActiveSelections() {
            document.querySelectorAll('.font-preview').forEach(el => el.classList.remove('active'));
            
            const selectors = [
                `[data-font="${currentFontCustomization.font}"]`,
                `[data-weight="${currentFontCustomization.weight}"]`,
                `[data-size="${currentFontCustomization.size}"]`,
                `[data-spacing="${currentFontCustomization.spacing}"]`,
                `[data-line-height="${currentFontCustomization.lineHeight}"]`
            ];
            
            selectors.forEach(selector => {
                const element = document.querySelector(selector);
                if (element) element.classList.add('active');
            });
            
            currentFontCustomization.effects.forEach(effect => {
                const element = document.querySelector(`[data-effect="${effect}"]`);
                if (element) element.classList.add('active');
            });
        }
        
        function applyFontCustomization() {
            window.currentElementFontClass = [
                currentFontCustomization.font,
                currentFontCustomization.weight,
                currentFontCustomization.size,
                currentFontCustomization.spacing,
                currentFontCustomization.lineHeight,
                ...currentFontCustomization.effects
            ].join(' ');
            
            closeModal('fontModal');
            alert('Font customization applied! ♥ Now add your text element to see it in action.');
        }
        
        function resetFontCustomization() {
            currentFontCustomization = {
                font: 'font-inter',
                weight: 'font-normal',
                size: 'text-base',
                effects: [],
                spacing: 'tracking-normal',
                lineHeight: 'leading-normal'
            };
            window.currentElementFontClass = '';
            updateFontPreview();
            updateActiveSelections();
        }
        
        function addTextToSite() {
            const content = document.getElementById('elementContent').value;
            const targetSection = document.getElementById('targetSection').value;
            const textStyle = document.getElementById('textStyle').value;
            const transparentMode = document.getElementById('transparentMode').checked;
            
            if (!content.trim()) {
                alert('Please enter some text!');
                return;
            }
            
            addContentToSection('text', {
                content: content,
                target: targetSection,
                style: textStyle,
                page: currentPage,
                transparent: transparentMode,
                fontClass: window.currentElementFontClass || ''
            });
        }
        
        function addImageToSite() {
            const imageFile = document.getElementById('imageFile').files[0];
            const targetSection = document.getElementById('targetSection').value;
            const caption = document.getElementById('imageCaption').value;
            const transparentMode = document.getElementById('transparentMode').checked;
            
            if (!imageFile) {
                alert('Please select an image!');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                addContentToSection('image', {
                    content: e.target.result,
                    target: targetSection,
                    caption: caption,
                    page: currentPage,
                    transparent: transparentMode
                });
            };
            reader.readAsDataURL(imageFile);
        }
        
        function addVideoToSite() {
            const videoFile = document.getElementById('videoFile').files[0];
            const targetSection = document.getElementById('targetSection').value;
            const videoControls = document.getElementById('videoControls').checked;
            const transparentMode = document.getElementById('transparentMode').checked;
            
            if (!videoFile) {
                alert('Please select a video or GIF!');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                addContentToSection('video', {
                    content: e.target.result,
                    target: targetSection,
                    page: currentPage,
                    controls: videoControls,
                    transparent: transparentMode
                });
            };
            reader.readAsDataURL(videoFile);
        }
        
        function addLabelToSite() {
            const labelText = document.getElementById('labelText').value;
            const targetSection = document.getElementById('targetSection').value;
            const labelStyle = document.getElementById('labelStyle').value;
            const transparentMode = document.getElementById('transparentMode').checked;
            
            if (!labelText.trim()) {
                alert('Please enter label text!');
                return;
            }
            
            addContentToSection('label', {
                content: labelText,
                target: targetSection,
                style: labelStyle,
                page: currentPage,
                transparent: transparentMode,
                fontClass: window.currentElementFontClass || ''
            });
        }
        
        function addDiscordToSite() {
            const discordUrl = document.getElementById('discordUrl').value;
            const targetSection = document.getElementById('targetSection').value;
            const discordTitle = document.getElementById('discordTitle').value || 'Discord Server';
            const discordHeight = document.getElementById('discordHeight').value;
            const transparentMode = document.getElementById('transparentMode').checked;
            
            if (!discordUrl.trim()) {
                alert('Please enter a Discord widget URL!');
                return;
            }
            
            if (!discordUrl.includes('discord.com') && !discordUrl.includes('discordapp.com')) {
                alert('Please enter a valid Discord widget URL (from Discord Server Settings → Widget)');
                return;
            }
            
            addContentToSection('discord', {
                content: discordUrl,
                target: targetSection,
                title: discordTitle,
                height: discordHeight,
                page: currentPage,
                transparent: transparentMode
            });
        }
        
        function addContentToSection(type, data) {
            fetch('/add-content-to-section', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    type: type,
                    data: data
                })
            }).then(response => response.json())
            .then(result => {
                if (result.success) {
                    closeModal('elementModal');
                    window.currentElementFontClass = '';
                    resetFontCustomization();
                    alert('Content added successfully! ♥');
                    location.reload();
                } else {
                    alert('Error adding content: ' + (result.error || 'Unknown error'));
                }
            }).catch(error => {
                console.error('Error:', error);
                alert('Error adding content!');
            });
        }
        
        // Right-click context menu for deletion
        function setupRightClickMenus() {
            document.addEventListener('contextmenu', function(e) {
                if (!document.body.classList.contains('edit-mode')) return;
                
                const editableElement = e.target.closest('.editable-element');
                if (!editableElement) return;
                
                e.preventDefault();
                showContextMenu(e, editableElement);
            });
            
            document.addEventListener('click', function(e) {
                const existingMenu = document.querySelector('.context-menu');
                if (existingMenu && !e.target.closest('.context-menu')) {
                    existingMenu.remove();
                }
            });
        }
        
        function showContextMenu(event, element) {
            const existingMenu = document.querySelector('.context-menu');
            if (existingMenu) existingMenu.remove();
            
            const menu = document.createElement('div');
            menu.className = 'context-menu';
            menu.style.cssText = `
                position: fixed;
                top: ${event.clientY}px;
                left: ${event.clientX}px;
                background: rgba(0, 0, 0, 0.9);
                border: 2px solid #ff69b4;
                border-radius: 8px;
                padding: 10px;
                z-index: 10000;
                min-width: 180px;
            `;
            
            const elementId = element.id;
            const currentLayer = getElementLayer(element);
            
            let menuContent = `
                <div style="color: #ff69b4; font-weight: bold; margin-bottom: 10px; text-align: center;">
                    Element Options (Layer ${currentLayer})
                </div>
                <button onclick="editElementInline('${elementId}')" style="width: 100%; margin-bottom: 5px;">
                    ✏️ Edit Content
                </button>
                <button onclick="copyElement('${elementId}')" style="width: 100%; margin-bottom: 5px;">
                    📋 Copy Element
                </button>
                <hr style="border-color: #ff69b4; margin: 5px 0;">
                <button onclick="sendElementToFront(document.getElementById('${elementId}'))" style="width: 100%; margin-bottom: 3px;">
                    ⬆️ Send to Front (5)
                </button>
                <button onclick="sendElementForward(document.getElementById('${elementId}'))" style="width: 100%; margin-bottom: 3px;">
                    ↗️ Send Forward (+1)
                </button>
                <button onclick="sendElementBackward(document.getElementById('${elementId}'))" style="width: 100%; margin-bottom: 3px;">
                    ↙️ Send Backward (-1)
                </button>
                <button onclick="sendElementToBack(document.getElementById('${elementId}'))" style="width: 100%; margin-bottom: 5px;">
                    ⬇️ Send to Back (1)
                </button>
                <hr style="border-color: #ff69b4; margin: 5px 0;">
                <button onclick="deleteElementConfirm('${elementId}')" class="btn-danger" style="width: 100%; margin-bottom: 5px;">
                    🗑️ Delete Element
                </button>
                <button onclick="closeContextMenu()" class="btn-secondary" style="width: 100%;">
                    ❌ Cancel
                </button>
            `;
            
            menu.innerHTML = menuContent;
            document.body.appendChild(menu);
        }
        
        function editElementInline(elementId) {
            closeContextMenu();
            const element = document.getElementById(elementId);
            if (!element) return;
            
            // Determine element type and content
            const elementType = detectElementType(element);
            openEditElementModal(elementId, elementType);
        }
        
        function detectElementType(element) {
            if (element.querySelector('img')) return 'image';
            if (element.querySelector('video')) return 'video';
            if (element.querySelector('iframe')) return 'discord';
            if (element.querySelector('label')) return 'label';
            return 'text';
        }
        
        function openEditElementModal(elementId, elementType) {
            const element = document.getElementById(elementId);
            const modal = document.getElementById('editElementModal');
            const form = document.getElementById('editElementForm');
            
            let formContent = '';
            
            switch(elementType) {
                case 'text':
                    const textContent = element.querySelector('p, h3, h4, div:not(.transform-handles):not(.element-overlay)')?.textContent || '';
                    formContent = `
                        <div class="form-group">
                            <label>Text Content:</label>
                            <textarea id="editElementContent">${textContent}</textarea>
                        </div>
                        <div class="form-group">
                            <label>Text Style:</label>
                            <select id="editTextStyle">
                                <option value="normal">Normal</option>
                                <option value="rainbow">Rainbow</option>
                                <option value="header">Header</option>
                                <option value="subtitle">Subtitle</option>
                            </select>
                        </div>
                        <button onclick="saveElementEdit('${elementId}', 'text')">Save Changes ♥</button>
                    `;
                    break;
                case 'image':
                    const imgSrc = element.querySelector('img')?.src || '';
                    const imgCaption = element.querySelector('p')?.textContent || '';
                    formContent = `
                        <div class="form-group">
                            <label>Current Image:</label>
                            <img src="${imgSrc}" style="max-width: 200px; max-height: 150px; border-radius: 5px;">
                        </div>
                        <div class="form-group">
                            <label>Replace Image:</label>
                            <input type="file" id="editImageFile" accept="image/*">
                        </div>
                        <div class="form-group">
                            <label>Caption:</label>
                            <input type="text" id="editImageCaption" value="${imgCaption}">
                        </div>
                        <button onclick="saveElementEdit('${elementId}', 'image')">Save Changes ♥</button>
                    `;
                    break;
                case 'label':
                    const labelContent = element.querySelector('label')?.textContent || '';
                    formContent = `
                        <div class="form-group">
                            <label>Label Text:</label>
                            <input type="text" id="editLabelContent" value="${labelContent}">
                        </div>
                        <button onclick="saveElementEdit('${elementId}', 'label')">Save Changes ♥</button>
                    `;
                    break;
                default:
                    formContent = '<p>This element type cannot be edited inline.</p>';
            }
            
            form.innerHTML = formContent;
            modal.style.display = 'block';
        }
        
        function saveElementEdit(elementId, elementType) {
            const element = document.getElementById(elementId);
            
            switch(elementType) {
                case 'text':
                    const newText = document.getElementById('editElementContent').value;
                    const textStyle = document.getElementById('editTextStyle').value;
                    const textElement = element.querySelector('p, h3, h4, div:not(.transform-handles):not(.element-overlay)');
                    if (textElement) {
                        textElement.textContent = newText;
                        // Apply style class
                        textElement.className = textStyle === 'rainbow' ? 'rainbow-text' : '';
                    }
                    break;
                case 'image':
                    const newCaption = document.getElementById('editImageCaption').value;
                    const captionElement = element.querySelector('p');
                    if (captionElement) {
                        captionElement.textContent = newCaption;
                    }
                    
                    const newImageFile = document.getElementById('editImageFile').files[0];
                    if (newImageFile) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const imgElement = element.querySelector('img');
                            if (imgElement) {
                                imgElement.src = e.target.result;
                            }
                        };
                        reader.readAsDataURL(newImageFile);
                    }
                    break;
                case 'label':
                    const newLabelText = document.getElementById('editLabelContent').value;
                    const labelElement = element.querySelector('label');
                    if (labelElement) {
                        labelElement.textContent = newLabelText;
                    }
                    break;
            }
            
            closeModal('editElementModal');
            saveElementToServer(elementId);
        }
        
        function copyElement(elementId) {
            closeContextMenu();
            const element = document.getElementById(elementId);
            if (!element) return;
            
            // Clone the element
            const clone = element.cloneNode(true);
            
            // Generate new ID
            const newId = 'copy-' + Date.now();
            clone.id = newId;
            
            // Offset position slightly
            const currentLeft = parseFloat(element.style.left) || 20;
            const currentTop = parseFloat(element.style.top) || 20;
            clone.style.left = (currentLeft + 20) + 'px';
            clone.style.top = (currentTop + 20) + 'px';
            
            // Add to page
            element.parentNode.appendChild(clone);
            
            // Setup transform handles for the copy
            if (document.body.classList.contains('edit-mode')) {
                setupTransformHandles(clone);
            }
            
            // Save to server
            saveElementToServer(newId);
            
            alert('Element copied! ♥');
        }
        
        function openLayerManager() {
            const modal = document.getElementById('layerModal');
            const layerList = document.getElementById('layerList');
            
            // Get all editable elements
            const elements = document.querySelectorAll('.editable-element');
            
            let layerContent = '';
            
            // Organize by layers
            for (let layer = 5; layer >= 1; layer--) {
                layerContent += `
                    <div style="margin: 15px 0; padding: 10px; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                        <h4 style="color: #ff69b4; margin-bottom: 10px;">Layer ${layer} ${layer === 5 ? '(Front)' : layer === 1 ? '(Back)' : ''}</h4>
                `;
                
                let hasElements = false;
                elements.forEach(element => {
                    const elementLayer = getElementLayer(element);
                    if (elementLayer === layer) {
                        hasElements = true;
                        const elementName = element.id || 'Unnamed Element';
                        const elementType = detectElementType(element);
                        layerContent += `
                            <div style="display: flex; justify-content: space-between; align-items: center; margin: 5px 0; padding: 5px; background: rgba(255, 105, 180, 0.1); border-radius: 5px;">
                                <span>${elementName} (${elementType})</span>
                                <div>
                                    <button onclick="selectElementById('${element.id}')" style="padding: 2px 6px; font-size: 12px;">Select</button>
                                    <button onclick="setElementLayer(document.getElementById('${element.id}'), ${Math.min(5, layer + 1)}); openLayerManager();" style="padding: 2px 6px; font-size: 12px;">↑</button>
                                    <button onclick="setElementLayer(document.getElementById('${element.id}'), ${Math.max(1, layer - 1)}); openLayerManager();" style="padding: 2px 6px; font-size: 12px;">↓</button>
                                </div>
                            </div>
                        `;
                    }
                });
                
                if (!hasElements) {
                    layerContent += '<p style="color: #888; font-style: italic;">No elements on this layer</p>';
                }
                
                layerContent += '</div>';
            }
            
            layerList.innerHTML = layerContent;
            modal.style.display = 'block';
        }
        
        function openElementManager() {
            const modal = document.getElementById('elementModal2');
            const elementsList = document.getElementById('elementsList');
            
            // Get all elements from all pages
            fetch('/get-all-elements')
            .then(response => response.json())
            .then(data => {
                let elementsContent = '';
                
                // Group by page
                Object.keys(data).forEach(page => {
                    elementsContent += `
                        <div style="margin: 15px 0; padding: 10px; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                            <h4 style="color: #ff69b4; margin-bottom: 10px;">Page: ${page || 'Home'}</h4>
                    `;
                    
                    if (data[page].length === 0) {
                        elementsContent += '<p style="color: #888; font-style: italic;">No custom elements on this page</p>';
                    } else {
                        data[page].forEach(element => {
                            elementsContent += `
                                <div style="display: flex; justify-content: space-between; align-items: center; margin: 5px 0; padding: 5px; background: rgba(255, 105, 180, 0.1); border-radius: 5px;">
                                    <span>${element.id} (${element.type})</span>
                                    <div>
                                        <button onclick="editCrossPageElement('${element.id}', '${page}')" style="padding: 2px 6px; font-size: 12px;">Edit</button>
                                        <button onclick="deleteCrossPageElement('${element.id}', '${page}')" class="btn-danger" style="padding: 2px 6px; font-size: 12px;">Delete</button>
                                    </div>
                                </div>
                            `;
                        });
                    }
                    
                    elementsContent += '</div>';
                });
                
                elementsList.innerHTML = elementsContent;
            })
            .catch(error => {
                console.error('Error loading elements:', error);
                elementsList.innerHTML = '<p style="color: #ff0000;">Error loading elements</p>';
            });
            
            modal.style.display = 'block';
        }
        
        function selectElementById(elementId) {
            const element = document.getElementById(elementId);
            if (element) {
                selectElement(element);
                closeModal('layerModal');
            }
        }
        
        function editCrossPageElement(elementId, page) {
            // Navigate to the page and then edit the element
            if (window.location.pathname !== page) {
                sessionStorage.setItem('editElementOnLoad', elementId);
                window.location.href = page;
            } else {
                const element = document.getElementById(elementId);
                if (element) {
                    selectElement(element);
                    editElementInline(elementId);
                }
                closeModal('elementModal2');
            }
        }
        
        function deleteCrossPageElement(elementId, page) {
            if (confirm(`Delete element ${elementId} from page ${page}?`)) {
                fetch('/delete-cross-page-element', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        elementId: elementId,
                        page: page
                    })
                }).then(() => {
                    openElementManager(); // Refresh the list
                    // If we're on the same page, remove from DOM
                    if (window.location.pathname === page) {
                        const element = document.getElementById(elementId);
                        if (element) {
                            element.remove();
                        }
                    }
                });
            }
        }
        
        function saveElementToServer(elementId) {
            const element = document.getElementById(elementId);
            if (!element) return;
            
            const elementData = {
                id: elementId,
                innerHTML: element.innerHTML,
                style: element.style.cssText,
                className: element.className,
                layer: getElementLayer(element)
            };
            
            fetch('/save-cross-page-element', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    elementId: elementId,
                    elementData: elementData,
                    page: window.location.pathname
                })
            }).catch(error => {
                console.error('Error saving element:', error);
            });
        }
        
        function editElementContent(elementId) {
            closeContextMenu();
            if (elementId.startsWith('section-')) {
                const sectionId = elementId.replace('section-', '');
                editSection(sectionId);
            } else {
                alert('Element editing coming soon!');
            }
        }
        
        function deleteElementConfirm(elementId) {
            closeContextMenu();
            
            if (confirm('Are you sure you want to delete this element and all its content?')) {
                if (elementId.startsWith('section-')) {
                    const sectionId = elementId.replace('section-', '');
                    deleteSection(sectionId);
                } else if (elementId.startsWith('custom-')) {
                    deleteElement(elementId);
                }
            }
        }
        
        function editSection(sectionId) {
            const newTitle = prompt('Edit section title:', 'Custom Section');
            if (newTitle !== null) {
                fetch('/update-section-title', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        sectionId: sectionId,
                        title: newTitle
                    })
                }).then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('Section updated! ♥');
                        location.reload();
                    } else {
                        alert('Error updating section: ' + (result.error || 'Unknown error'));
                    }
                });
            }
        }
        
        function deleteSection(sectionId) {
            fetch('/delete-section', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({sectionId: sectionId})
            }).then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('Section deleted! ♥');
                    location.reload();
                } else {
                    alert('Error deleting section: ' + (result.error || 'Unknown error'));
                }
            });
        }
        
        function deleteElement(elementId) {
            fetch('/delete-custom-element', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({elementId: elementId})
            }).then(() => {
                alert('Element deleted!');
                location.reload();
            });
        }
        
        function toggleGrid() {
            document.body.classList.toggle('show-grid');
            const button = document.getElementById('gridToggle');
            if (document.body.classList.contains('show-grid')) {
                button.textContent = 'Hide Grid';
                button.className = 'btn-success';
            } else {
                button.textContent = 'Show Grid';
                button.className = 'btn-secondary';
            }
        }
        
        function resetAllTransforms() {
            if (confirm('Reset all element positions and sizes to default? This cannot be undone.')) {
                fetch('/reset-all-transforms', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({page: window.location.pathname})
                }).then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('All transforms reset! ♥');
                        location.reload();
                    } else {
                        alert('Error resetting transforms: ' + (data.error || 'Unknown error'));
                    }
                }).catch(error => {
                    console.error('Error:', error);
                    alert('Error resetting transforms!');
                });
            }
        }
        
        function previewMode() {
            document.body.classList.remove('edit-mode');
            alert('Preview mode for 5 seconds...');
            setTimeout(() => {
                document.body.classList.add('edit-mode');
            }, 5000);
        }
        
        // Floating hearts animation
        function createHeart() {
            const heart = document.createElement('div');
            heart.className = 'heart';
            heart.innerHTML = '♥';
            heart.style.left = Math.random() * 100 + 'vw';
            heart.style.animationDuration = (Math.random() * 3 + 4) + 's';
            heart.style.fontSize = (Math.random() * 10 + 15) + 'px';
            document.body.appendChild(heart);
            
            setTimeout(() => {
                heart.remove();
            }, 6000);
        }
        
        setInterval(createHeart, 3000);
        
        // Advanced Transform System
        let selectedElement = null;
        let transformState = {
            isTransforming: false,
            mode: null,
            startX: 0,
            startY: 0,
            startWidth: 0,
            startHeight: 0,
            startLeft: 0,
            startTop: 0,
            startRotation: 0,
            handle: null
        };
        
        function initTransformSystem() {
            if (!document.body.classList.contains('edit-mode')) return;
            
            if (!document.querySelector('.grid-overlay')) {
                const gridOverlay = document.createElement('div');
                gridOverlay.className = 'grid-overlay';
                document.body.appendChild(gridOverlay);
            }
            
            const editableElements = document.querySelectorAll('.editable-element');
            editableElements.forEach(element => {
                setupTransformHandles(element);
            });
            
            document.addEventListener('mousedown', handleTransformStart);
            document.addEventListener('mousemove', handleTransformMove);
            document.addEventListener('mouseup', handleTransformEnd);
            document.addEventListener('keydown', handleKeyboardShortcuts);
        }
        
        function setupTransformHandles(element) {
            const existingHandles = element.querySelector('.transform-handles');
            if (existingHandles) {
                existingHandles.remove();
            }
            
            const handlesContainer = document.createElement('div');
            handlesContainer.className = 'transform-handles';
            handlesContainer.innerHTML = `
                <div class="transform-handle handle-nw" data-handle="nw"></div>
                <div class="transform-handle handle-ne" data-handle="ne"></div>
                <div class="transform-handle handle-sw" data-handle="sw"></div>
                <div class="transform-handle handle-se" data-handle="se"></div>
                <div class="transform-handle handle-n" data-handle="n"></div>
                <div class="transform-handle handle-s" data-handle="s"></div>
                <div class="transform-handle handle-e" data-handle="e"></div>
                <div class="transform-handle handle-w" data-handle="w"></div>
                <div class="transform-handle handle-move" data-handle="move" title="Drag to move"></div>
                <div class="transform-handle handle-rotate" data-handle="rotate" title="Drag to rotate"></div>
                <div class="transform-info"></div>
                <div class="layer-indicator">${getElementLayer(element)}</div>
            `;
            
            element.appendChild(handlesContainer);
            
            element.style.position = 'absolute';
            if (!element.style.left) element.style.left = '20px';
            if (!element.style.top) element.style.top = '20px';
            if (!element.style.width) element.style.width = 'auto';
            if (!element.style.minWidth) element.style.minWidth = '200px';
            if (!element.style.minHeight) element.style.minHeight = '100px';
            
            // Apply layer class
            applyElementLayer(element, getElementLayer(element));
        }
        
        function handleTransformStart(e) {
            if (!document.body.classList.contains('edit-mode')) return;
            
            const handle = e.target.closest('.transform-handle');
            const element = e.target.closest('.editable-element');
            
            if (handle && element) {
                e.preventDefault();
                e.stopPropagation();
                
                selectedElement = element;
                selectedElement.classList.add('transforming');
                
                const rect = element.getBoundingClientRect();
                const containerRect = element.offsetParent.getBoundingClientRect();
                
                transformState = {
                    isTransforming: true,
                    mode: getTransformMode(handle.dataset.handle),
                    handle: handle.dataset.handle,
                    startX: e.clientX,
                    startY: e.clientY,
                    startWidth: rect.width,
                    startHeight: rect.height,
                    startLeft: rect.left - containerRect.left,
                    startTop: rect.top - containerRect.top,
                    startRotation: getElementRotation(element)
                };
                
                document.body.classList.add('show-grid');
                updateTransformInfo();
            } else if (element && !handle) {
                selectElement(element);
            } else {
                deselectElement();
            }
        }
        
        function handleTransformMove(e) {
            if (!transformState.isTransforming || !selectedElement) return;
            
            e.preventDefault();
            
            const deltaX = e.clientX - transformState.startX;
            const deltaY = e.clientY - transformState.startY;
            
            switch (transformState.mode) {
                case 'move':
                    handleMove(deltaX, deltaY);
                    break;
                case 'resize':
                    handleResize(deltaX, deltaY);
                    break;
                case 'rotate':
                    handleRotate(e);
                    break;
            }
            
            updateTransformInfo();
        }
        
        function handleTransformEnd(e) {
            if (!transformState.isTransforming) return;
            
            transformState.isTransforming = false;
            document.body.classList.remove('show-grid');
            
            if (selectedElement) {
                selectedElement.classList.remove('transforming');
                saveElementTransform(selectedElement);
            }
        }
        
        function getTransformMode(handleType) {
            if (handleType === 'move') return 'move';
            if (handleType === 'rotate') return 'rotate';
            return 'resize';
        }
        
        function handleMove(deltaX, deltaY) {
            const newLeft = transformState.startLeft + deltaX;
            const newTop = transformState.startTop + deltaY;
            
            const gridSize = 10;
            const snappedLeft = Math.round(newLeft / gridSize) * gridSize;
            const snappedTop = Math.round(newTop / gridSize) * gridSize;
            
            selectedElement.style.left = snappedLeft + 'px';
            selectedElement.style.top = snappedTop + 'px';
        }
        
        function handleResize(deltaX, deltaY) {
            const handle = transformState.handle;
            let newWidth = transformState.startWidth;
            let newHeight = transformState.startHeight;
            let newLeft = transformState.startLeft;
            let newTop = transformState.startTop;
            
            switch (handle) {
                case 'se':
                    newWidth = Math.max(100, transformState.startWidth + deltaX);
                    newHeight = Math.max(50, transformState.startHeight + deltaY);
                    break;
                case 'sw':
                    newWidth = Math.max(100, transformState.startWidth - deltaX);
                    newHeight = Math.max(50, transformState.startHeight + deltaY);
                    newLeft = transformState.startLeft + deltaX;
                    break;
                case 'ne':
                    newWidth = Math.max(100, transformState.startWidth + deltaX);
                    newHeight = Math.max(50, transformState.startHeight - deltaY);
                    newTop = transformState.startTop + deltaY;
                    break;
                case 'nw':
                    newWidth = Math.max(100, transformState.startWidth - deltaX);
                    newHeight = Math.max(50, transformState.startHeight - deltaY);
                    newLeft = transformState.startLeft + deltaX;
                    newTop = transformState.startTop + deltaY;
                    break;
                case 'e':
                    newWidth = Math.max(100, transformState.startWidth + deltaX);
                    break;
                case 'w':
                    newWidth = Math.max(100, transformState.startWidth - deltaX);
                    newLeft = transformState.startLeft + deltaX;
                    break;
                case 's':
                    newHeight = Math.max(50, transformState.startHeight + deltaY);
                    break;
                case 'n':
                    newHeight = Math.max(50, transformState.startHeight - deltaY);
                    newTop = transformState.startTop + deltaY;
                    break;
            }
            
            selectedElement.style.width = newWidth + 'px';
            selectedElement.style.height = newHeight + 'px';
            selectedElement.style.left = newLeft + 'px';
            selectedElement.style.top = newTop + 'px';
            
            // Special handling for text elements - resize the actual text
            if (isTextElement(selectedElement)) {
                resizeTextContent(selectedElement, newWidth, newHeight);
            }
        }
        
        function isTextElement(element) {
            // Check if element contains primarily text content
            const hasText = element.querySelector('p, h1, h2, h3, h4, h5, h6, span, div:not(.transform-handles):not(.element-overlay)');
            const hasMedia = element.querySelector('img, video, iframe');
            return hasText && !hasMedia;
        }
        
        function resizeTextContent(element, newWidth, newHeight) {
            // Calculate scale factor based on container resize
            const startWidth = transformState.startWidth;
            const startHeight = transformState.startHeight;
            const scaleX = newWidth / startWidth;
            const scaleY = newHeight / startHeight;
            const scale = Math.min(scaleX, scaleY); // Use smaller scale to maintain aspect ratio
            
            // Find text elements and scale their font size
            const textElements = element.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, div:not(.transform-handles):not(.element-overlay)');
            
            textElements.forEach(textEl => {
                if (!textEl.dataset.originalFontSize) {
                    // Store original font size
                    const computedStyle = window.getComputedStyle(textEl);
                    textEl.dataset.originalFontSize = parseFloat(computedStyle.fontSize);
                }
                
                const originalSize = parseFloat(textEl.dataset.originalFontSize);
                const newSize = Math.max(8, originalSize * scale); // Minimum 8px font size
                textEl.style.fontSize = newSize + 'px';
            });
        }
        
        // Layer Management System
        function getElementLayer(element) {
            // Extract layer from class or default to 3 (middle)
            for (let i = 1; i <= 5; i++) {
                if (element.classList.contains(`layer-${i}`)) {
                    return i;
                }
            }
            return 3; // Default middle layer
        }
        
        function setElementLayer(element, layer) {
            // Remove existing layer classes
            for (let i = 1; i <= 5; i++) {
                element.classList.remove(`layer-${i}`);
            }
            
            // Add new layer class
            layer = Math.max(1, Math.min(5, layer)); // Clamp between 1-5
            element.classList.add(`layer-${layer}`);
            
            // Update layer indicator
            const indicator = element.querySelector('.layer-indicator');
            if (indicator) {
                indicator.textContent = layer;
            }
            
            // Save to server
            saveElementLayer(element, layer);
        }
        
        function applyElementLayer(element, layer) {
            setElementLayer(element, layer);
        }
        
        function saveElementLayer(element, layer) {
            const elementId = element.id;
            fetch('/save-element-layer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    elementId: elementId,
                    layer: layer
                })
            }).catch(error => {
                console.error('Error saving element layer:', error);
            });
        }
        
        function sendElementForward(element) {
            const currentLayer = getElementLayer(element);
            if (currentLayer < 5) {
                setElementLayer(element, currentLayer + 1);
            }
        }
        
        function sendElementBackward(element) {
            const currentLayer = getElementLayer(element);
            if (currentLayer > 1) {
                setElementLayer(element, currentLayer - 1);
            }
        }
        
        function sendElementToFront(element) {
            setElementLayer(element, 5);
        }
        
        function sendElementToBack(element) {
            setElementLayer(element, 1);
        }
        
        function handleRotate(e) {
            const rect = selectedElement.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX);
            const rotation = (angle * 180 / Math.PI);
            
            selectedElement.style.transform = `rotate(${rotation}deg)`;
        }
        
        function selectElement(element) {
            deselectElement();
            selectedElement = element;
            element.classList.add('transforming');
            
            if (!element.querySelector('.transform-handles')) {
                setupTransformHandles(element);
            }
        }
        
        function deselectElement() {
            if (selectedElement) {
                selectedElement.classList.remove('transforming');
                selectedElement = null;
            }
        }
        
        function updateTransformInfo() {
            if (!selectedElement) return;
            
            const infoElement = selectedElement.querySelector('.transform-info');
            if (!infoElement) return;
            
            const rect = selectedElement.getBoundingClientRect();
            const rotation = getElementRotation(selectedElement);
            
            infoElement.innerHTML = `
                W: ${Math.round(rect.width)}px 
                H: ${Math.round(rect.height)}px 
                X: ${Math.round(parseFloat(selectedElement.style.left))}px 
                Y: ${Math.round(parseFloat(selectedElement.style.top))}px
                ${rotation !== 0 ? ` R: ${Math.round(rotation)}°` : ''}
            `;
        }
        
        function getElementRotation(element) {
            const transform = element.style.transform;
            if (!transform) return 0;
            
            const match = transform.match(/rotate\(([^)]+)deg\)/);
            return match ? parseFloat(match[1]) : 0;
        }
        
        function handleKeyboardShortcuts(e) {
            if (!document.body.classList.contains('edit-mode') || !selectedElement) return;
            
            switch (e.key) {
                case 'Delete':
                case 'Backspace':
                    e.preventDefault();
                    showContextMenu({clientX: 0, clientY: 0}, selectedElement);
                    break;
                case 'Escape':
                    deselectElement();
                    break;
                case 'g':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        document.body.classList.toggle('show-grid');
                    }
                    break;
            }
        }
        
        function saveElementTransform(element) {
            const elementId = element.id;
            const rotation = getElementRotation(element);
            
            const transformData = {
                left: element.style.left,
                top: element.style.top,
                width: element.style.width,
                height: element.style.height,
                transform: element.style.transform
            };
            
            fetch('/save-element-transform', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    elementId: elementId,
                    transform: transformData
                })
            }).catch(error => {
                console.error('Error saving transform:', error);
            });
        }
        
        // Modal functions
        function openModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        // User context menu for moderation
        function showUserActions(event, username, currentRole) {
            event.preventDefault();
            const userRole = '{{ session.get("role", "") }}';
            
            if (userRole !== 'admin' && userRole !== 'host') return;
            if (username === '{{ session.get("username", "") }}') return;
            
            const existingMenu = document.querySelector('.user-actions');
            if (existingMenu) existingMenu.remove();
            
            const menu = document.createElement('div');
            menu.className = 'user-actions';
            menu.style.display = 'block';
            menu.style.left = event.pageX + 'px';
            menu.style.top = event.pageY + 'px';
            
            let actions = '';
            if (userRole === 'admin') {
                actions = `
                    <button onclick="banUser('${username}')">Ban User</button>
                    <button onclick="changeRole('${username}', 'admin')">Make Admin</button>
                    <button onclick="changeRole('${username}', 'host')">Make Host</button>
                    <button onclick="changeRole('${username}', 'guest')">Make Guest</button>
                `;
            } else if (userRole === 'host' && currentRole === 'guest') {
                actions = `<button onclick="banUser('${username}')">Ban User</button>`;
            }
            
            menu.innerHTML = actions + '<button onclick="this.parentElement.remove()">Cancel</button>';
            document.body.appendChild(menu);
        }
        
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.user-actions')) {
                const menu = document.querySelector('.user-actions');
                if (menu) menu.remove();
            }
        });
        
        function banUser(username) {
            if (confirm(`Are you sure you want to ban ${username}?`)) {
                fetch('/ban-user', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username: username})
                }).then(() => location.reload());
            }
        }
        
        function changeRole(username, role) {
            fetch('/change-role', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username, role: role})
            }).then(() => location.reload());
        }
        
        function viewProfile(username) {
            window.location.href = `/view-profile/${username}`;
        }
        
        // Initialize everything
        window.addEventListener('load', () => {
            console.log('🏳️‍🌈 Gay Agenda Server Loaded! ♥');
            initPersistentMusic();
            initTransformSystem();
            setupRightClickMenus();
            
            // Load element layers
            loadElementLayers();
            
            // Check if we need to edit an element after page load
            const editElementId = sessionStorage.getItem('editElementOnLoad');
            if (editElementId) {
                sessionStorage.removeItem('editElementOnLoad');
                setTimeout(() => {
                    const element = document.getElementById(editElementId);
                    if (element) {
                        selectElement(element);
                        editElementInline(editElementId);
                    }
                }, 1000);
            }
            
            if (document.body.classList.contains('edit-mode')) {
                console.log('🎨 EDIT MODE ACTIVE!');
                console.log('📚 5-Layer System Available!');
                console.log('🎯 Enhanced Right-Click: Edit/Copy/Layers!');
                console.log('✏️ Text Resize: Properly scales font size!');
                console.log('🗂️ Cross-Page Element Management!');
            }
            
            const savedSoundVolume = localStorage.getItem('gayAgendaSoundVolume');
            if (savedSoundVolume) {
                const sound = document.getElementById('click-sound');
                if (sound) {
                    sound.volume = savedSoundVolume;
                    const volumeSlider = document.getElementById('sound-volume');
                    if (volumeSlider) {
                        volumeSlider.value = savedSoundVolume;
                    }
                }
            }
        });
        
        function loadElementLayers() {
            // Apply saved layers to elements
            fetch('/get-element-layers')
            .then(response => response.json())
            .then(layers => {
                Object.keys(layers).forEach(elementId => {
                    const element = document.getElementById(elementId);
                    if (element) {
                        applyElementLayer(element, layers[elementId]);
                    }
                });
            })
            .catch(error => {
                console.log('No saved layers found, using defaults');
            });
        }
        
        function closeContextMenu() {
            const menu = document.querySelector('.context-menu');
            if (menu) menu.remove();
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    settings = load_settings()
    custom_elements = load_custom_elements()
    site_sections = load_json_file(os.path.join(SCRIPT_DIR, 'site_sections.json'), {})
    transforms = load_json_file(os.path.join(SCRIPT_DIR, 'element_transforms.json'), {})
    
    def apply_transform(element_id, base_style="position: relative; margin: 20px 0;"):
        if element_id in transforms:
            transform = transforms[element_id]
            style_parts = []
            
            style_parts.append("position: absolute;")
            
            if transform.get('left'):
                style_parts.append(f"left: {transform['left']};")
            if transform.get('top'):
                style_parts.append(f"top: {transform['top']};")
            if transform.get('width'):
                style_parts.append(f"width: {transform['width']};")
            if transform.get('height'):
                style_parts.append(f"height: {transform['height']};")
            if transform.get('transform'):
                style_parts.append(f"transform: {transform['transform']};")
            
            return " ".join(style_parts)
        return base_style
    
    if settings.get('edit_mode'):
        content = f'''
            <div class="editable-element" id="welcome" data-type="content" style="{apply_transform('welcome')}">
                <div class="element-overlay"></div>
                <div class="fc-info pride-border">
                    <h3 class="rainbow-text">Welcome to the Gays!</h3>
                    <p>{settings['welcome_message']}</p>
                </div>
            </div>
            
            <div class="editable-element" id="about" data-type="content" style="{apply_transform('about')}">
                <div class="element-overlay"></div>
                <div class="fc-info">
                    <h3 class="rainbow-text">Our Location</h3>
                    <p>{settings['about_text']}</p>
                </div>
            </div>
            
            <div class="editable-element" id="join" data-type="content" style="{apply_transform('join')}">
                <div class="element-overlay"></div>
                <div class="fc-info">
                    <h3>♥ Mare ♥</h3>
                    <br/>
                    <h3 class="rainbow-text"> ID: MSS-5TYBMJDA7BP9 </h3>
                    <h3 class="rainbow-text"> PW: H1RZRDM8XPL6C6JW </h3>
                </div>
            </div>
        '''
        
        for section_id, section in site_sections.items():
            has_transparent = any(item.get('transparent', False) for item in section.get('content', []))
            section_class = 'transparent-element' if has_transparent else ''
            
            content += f'''
                <div class="editable-element {section_class}" id="section-{section_id}" data-type="custom-section" style="{apply_transform(f'section-{section_id}')}">
                    <div class="element-overlay"></div>
                    <div class="{'fc-info' if not has_transparent else ''}">
                        <h3 class="rainbow-text">{section.get('title', 'Custom Section')}</h3>
                        {render_section_content(section.get('content', []))}
                    </div>
                </div>
            '''
    else:
        header_style = apply_transform('header', 'text-align: center; margin-bottom: 40px;')
        welcome_style = apply_transform('welcome', 'margin: 20px 0;')
        about_style = apply_transform('about', 'margin: 20px 0;')
        join_style = apply_transform('join', 'margin: 20px 0;')
        
        content = f'''
            <div class="header" id="header" style="{header_style}">
                <h1 class="rainbow-text">{settings['site_title']}</h1>
                <h2>{settings['fc_name']} - {settings['server']}</h2>
            </div>
            
            <div class="fc-info pride-border" id="welcome" style="{welcome_style}">
                <h3 class="rainbow-text">Welcome to the Gays!</h3>
                <p>{settings['welcome_message']}</p>
            </div>
            
            <div class="fc-info" id="about" style="{about_style}">
                <h3 class="rainbow-text">Our Location</h3>
                <p>{settings['about_text']}</p>
            </div>
            
            <div class="fc-info" id="join" style="{join_style}">
                <h3>♥ Mare ♥</h3>
                <br/>
                <h3 class="rainbow-text"> ID: MSS-5TYBMJDA7BP9 </h3>
                <h3 class="rainbow-text"> PW: H1RZRDM8XPL6C6JW </h3>
            </div>
        '''
        
        for section_id, section in site_sections.items():
            has_transparent = any(item.get('transparent', False) for item in section.get('content', []))
            section_class = 'transparent-element' if has_transparent else 'fc-info'
            section_style = apply_transform(f'section-{section_id}', 'margin: 20px 0;')
            
            content += f'''
                <div class="{section_class}" id="section-{section_id}" style="{section_style}">
                    <h3 class="rainbow-text">{section.get('title', 'Custom Section')}</h3>
                    {render_section_content(section.get('content', []))}
                </div>
            '''
    
    return render_template_string(HTML_TEMPLATE, settings=settings, content=content, session=session, custom_elements=custom_elements)

def render_section_content(content_items):
    """Render the content items for a section"""
    html = ""
    for item in content_items:
        is_transparent = item.get('transparent', False)
        font_class = item.get('fontClass', '')
        
        if item['type'] == 'text':
            style_class = font_class
            if item.get('style') == 'rainbow' and not font_class:
                style_class = 'rainbow-text'
            elif item.get('style') == 'header':
                html += f'<h3 class="{style_class}">{item["text"]}</h3>'
                continue
            elif item.get('style') == 'subtitle':
                html += f'<h4 class="{style_class}">{item["text"]}</h4>'
                continue
            
            if is_transparent:
                html += f'<div style="background: none; padding: 0; margin: 0; display: inline-block;" class="{style_class}">{item["text"]}</div>'
            else:
                html += f'<p class="{style_class}">{item["text"]}</p>'
                
        elif item['type'] == 'image':
            caption = f'<p style="text-align: center; font-style: italic; margin-top: 5px;">{item["caption"]}</p>' if item.get('caption') and not is_transparent else ''
            
            if is_transparent:
                html += f'''
                    <div style="text-align: center; margin: 0; padding: 0; background: none;">
                        <img src="{item["image_data"]}" style="max-width: 100%; height: auto; border: none; background: transparent;" alt="Decorative Image">
                        {caption}
                    </div>
                '''
            else:
                html += f'''
                    <div style="text-align: center; margin: 15px 0;">
                        <img src="{item["image_data"]}" style="max-width: 100%; height: auto; border-radius: 10px; border: 2px solid #ff69b4;" alt="Custom Image">
                        {caption}
                    </div>
                '''
                
        elif item['type'] == 'video':
            controls_attr = 'controls' if item.get('controls', True) else 'autoplay muted loop'
            
            if is_transparent:
                html += f'''
                    <div style="text-align: center; margin: 0; padding: 0; background: none;">
                        <video {controls_attr} style="max-width: 100%; height: auto; border: none; background: transparent;">
                            <source src="{item["video_data"]}" type="video/mp4">
                        </video>
                    </div>
                '''
            else:
                html += f'''
                    <div style="text-align: center; margin: 15px 0;">
                        <video {controls_attr} style="max-width: 100%; height: auto; border-radius: 10px; border: 2px solid #ff69b4;">
                            <source src="{item["video_data"]}" type="video/mp4">
                        </video>
                    </div>
                '''
                
        elif item['type'] == 'label':
            style_class = font_class
            if item.get('style') == 'rainbow' and not font_class:
                style_class = 'rainbow-text'
            elif item.get('style') == 'bold':
                style_class += ' font-bold'
            elif item.get('style') == 'italic':
                style_class += ' text-italic'
            
            if is_transparent:
                html += f'<span class="{style_class}" style="color: #ff69b4; display: inline-block; margin: 0; padding: 0; background: none;">{item["text"]}</span>'
            else:
                html += f'<label class="{style_class}" style="color: #ff69b4; display: block; margin: 10px 0;">{item["text"]}</label>'
        
        elif item['type'] == 'discord':
            discord_url = item.get('discord_url', '')
            title = item.get('title', 'Discord Announcements')
            height = item.get('height', '400px')
            
            if is_transparent:
                html += f'''
                    <div style="margin: 10px 0; background: none; border: none;">
                        <iframe src="{discord_url}" 
                                width="100%" 
                                height="{height}" 
                                style="border: none; background: transparent; border-radius: 0;" 
                                frameborder="0" 
                                sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts">
                        </iframe>
                    </div>
                '''
            else:
                html += f'''
                    <div style="margin: 15px 0; background: rgba(114, 137, 218, 0.1); border-radius: 10px; padding: 10px; border: 2px solid #7289DA;">
                        <h4 style="color: #7289DA; margin-bottom: 10px;">{title}</h4>
                        <iframe src="{discord_url}" 
                                width="100%" 
                                height="{height}" 
                                style="border: none; border-radius: 8px;" 
                                frameborder="0" 
                                sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts">
                        </iframe>
                    </div>
                '''
    
    return html

# ALL THE WORKING ROUTES FROM THE OLDER VERSION
@app.route('/toggle-edit-mode', methods=['POST'])
def toggle_edit_mode():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    settings = load_settings()
    settings['edit_mode'] = not settings.get('edit_mode', False)
    save_settings(settings)
    
    return jsonify({'success': True, 'edit_mode': settings['edit_mode']})

@app.route('/update-site-content', methods=['POST'])
def update_site_content():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        
        settings = load_settings()
        
        if key in ['welcome_message', 'about_text', 'site_title', 'fc_name', 'server']:
            settings[key] = value
            save_settings(settings)
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Invalid setting key'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/save-element-transform', methods=['POST'])
def save_element_transform():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        element_id = data.get('elementId')
        transform_data = data.get('transform')
        
        transforms_file = os.path.join(SCRIPT_DIR, 'element_transforms.json')
        transforms = load_json_file(transforms_file, {})
        
        transforms[element_id] = {
            'left': transform_data.get('left'),
            'top': transform_data.get('top'),
            'width': transform_data.get('width'),
            'height': transform_data.get('height'),
            'transform': transform_data.get('transform'),
            'updated_at': datetime.now().isoformat()
        }
        
        save_json_file(transforms_file, transforms)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/reset-all-transforms', methods=['POST'])
def reset_all_transforms():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        transforms_file = os.path.join(SCRIPT_DIR, 'element_transforms.json')
        transforms = load_json_file(transforms_file, {})
        transforms.clear()
        save_json_file(transforms_file, transforms)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/add-content-to-section', methods=['POST'])
def add_content_to_section():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        content_type = data.get('type')
        content_data = data.get('data')
        
        page = content_data.get('page', '/')
        page_suffix = ''
        if page == '/characters':
            page_suffix = '_characters'
        elif page == '/messages':
            page_suffix = '_messages'
        elif page == '/suggestions':
            page_suffix = '_suggestions'
        elif page == '/profile':
            page_suffix = '_profile'
        elif page == '/admin':
            page_suffix = '_admin'
        elif page == '/manage-users':
            page_suffix = '_manage-users'
        
        sections_file = os.path.join(SCRIPT_DIR, f'site_sections{page_suffix}.json')
        if page == '/':
            sections_file = os.path.join(SCRIPT_DIR, 'site_sections.json')
        
        sections = load_json_file(sections_file, {})
        
        target_section = content_data.get('target')
        
        if target_section == 'new':
            section_id = str(uuid.uuid4())
            sections[section_id] = {
                'title': 'Custom Section',
                'content': []
            }
            target_section = section_id
        
        if target_section not in sections:
            sections[target_section] = {
                'title': 'Custom Section',
                'content': []
            }
        
        new_content = {'type': content_type}
        
        if content_type == 'text':
            new_content.update({
                'text': content_data['content'],
                'style': content_data.get('style', 'normal'),
                'transparent': content_data.get('transparent', False),
                'fontClass': content_data.get('fontClass', '')
            })
        elif content_type == 'image':
            new_content.update({
                'image_data': content_data['content'],
                'caption': content_data.get('caption', ''),
                'transparent': content_data.get('transparent', False)
            })
        elif content_type == 'video':
            new_content.update({
                'video_data': content_data['content'],
                'controls': content_data.get('controls', True),
                'transparent': content_data.get('transparent', False)
            })
        elif content_type == 'label':
            new_content.update({
                'text': content_data['content'],
                'style': content_data.get('style', 'normal'),
                'transparent': content_data.get('transparent', False),
                'fontClass': content_data.get('fontClass', '')
            })
        elif content_type == 'discord':
            new_content.update({
                'discord_url': content_data['content'],
                'title': content_data.get('title', 'Discord Server'),
                'height': content_data.get('height', '400px'),
                'transparent': content_data.get('transparent', False)
            })
        
        sections[target_section]['content'].append(new_content)
        save_json_file(sections_file, sections)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/update-section-title', methods=['POST'])
def update_section_title():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        section_id = data.get('sectionId')
        title = data.get('title')
        
        for page_suffix in ['', '_characters', '_messages', '_suggestions', '_profile', '_admin', '_manage-users']:
            sections_file = os.path.join(SCRIPT_DIR, f'site_sections{page_suffix}.json')
            sections = load_json_file(sections_file, {})
            
            if section_id in sections:
                sections[section_id]['title'] = title
                save_json_file(sections_file, sections)
                return jsonify({'success': True})
        
        return jsonify({'error': 'Section not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/delete-section', methods=['POST'])
def delete_section():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        section_id = data.get('sectionId')
        
        for page_suffix in ['', '_characters', '_messages', '_suggestions', '_profile', '_admin', '_manage-users']:
            sections_file = os.path.join(SCRIPT_DIR, f'site_sections{page_suffix}.json')
            sections = load_json_file(sections_file, {})
            
            if section_id in sections:
                del sections[section_id]
                save_json_file(sections_file, sections)
                return jsonify({'success': True})
        
        return jsonify({'error': 'Section not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/delete-custom-element', methods=['POST'])
def delete_custom_element():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    element_id = data.get('elementId')
    
    elements = load_custom_elements()
    elements = [el for el in elements if f"custom-{el['id']}" != element_id]
    save_custom_elements(elements)
    
    return jsonify({'success': True})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required!', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
        else:
            users = load_users()
            if username in users:
                flash('Username already exists!', 'error')
            else:
                users[username] = {
                    'password_hash': generate_password_hash(password),
                    'role': 'guest',
                    'created_at': datetime.now().isoformat(),
                    'banned': False
                }
                save_users(users)
                flash('Registration successful! You can now login.', 'success')
                return redirect(url_for('login'))
    
    settings = load_settings()
    custom_elements = load_custom_elements()
    content = '''
        <div class="register-form">
            <h2 class="rainbow-text" style="text-align: center; margin-bottom: 20px;">Join Our FC! ♥</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password (min 6 characters):</label>
                    <input type="password" id="password" name="password" required minlength="6">
                </div>
                <div style="text-align: center;">
                    <button type="submit">Register ♥</button>
                </div>
            </form>
        </div>
    '''
    return render_template_string(HTML_TEMPLATE, settings=settings, content=content, session=session, custom_elements=custom_elements)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        
        if username in users and not users[username].get('banned', False):
            if check_password_hash(users[username]['password_hash'], password):
                session['username'] = username
                session['role'] = users[username].get('role', 'guest')
                flash('Login successful! ♥', 'success')
                return redirect(url_for('home'))
        
        flash('Invalid credentials or account banned!', 'error')
    
    settings = load_settings()
    custom_elements = load_custom_elements()
    content = '''
        <div class="login-form">
            <h2 class="rainbow-text" style="text-align: center; margin-bottom: 20px;">Welcome Back! ♥</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <div style="text-align: center;">
                    <button type="submit">Login ♥</button>
                </div>
            </form>
        </div>
    '''
    return render_template_string(HTML_TEMPLATE, settings=settings, content=content, session=session, custom_elements=custom_elements)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully! ♥', 'success')
    return redirect(url_for('home'))

@app.route('/characters')
def characters():
    profiles = load_profiles()
    users = load_users()
    settings = load_settings()
    custom_elements = load_custom_elements()
    
    characters_html = ''
    for username, profile in profiles.items():
        if not profile.get('character_name'):
            continue
            
        user_role = users.get(username, {}).get('role', 'guest')
        badge_class = f'badge-{user_role}'
        
        image_html = ''
        if profile.get('character_image'):
            image_html = f'<img src="{profile["character_image"]}" class="character-image" alt="Character Image">'
        else:
            image_html = '<div class="character-image" style="background: rgba(255,105,180,0.2); display: flex; align-items: center; justify-content: center;">No Image</div>'
        
        characters_html += f'''
            <div class="character-profile" onclick="viewProfile('{username}')">
                {image_html}
                <div class="character-info">
                    <h3>{profile['character_name']} <span class="user-badge {badge_class}">{user_role}</span></h3>
                    <p><strong>Player:</strong> {username}</p>
                    <p><strong>Bio:</strong></p>
                    <p>{profile.get('character_bio', 'No bio available.')[:100]}{'...' if len(profile.get('character_bio', '')) > 100 else ''}</p>
                    <small style="color: #ff69b4;">Click to view full profile ♥</small>
                </div>
            </div>
        '''
    
    if not characters_html:
        characters_html = '<p style="text-align: center; color: #ff69b4;">No character profiles yet! ♥</p>'
    
    content = f'''
        <div class="user-panel">
            <h2 class="rainbow-text">FC Character Profiles ♥</h2>
            {characters_html}
        </div>
    '''
    return render_template_string(HTML_TEMPLATE, settings=settings, content=content, session=session, custom_elements=custom_elements)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if not session.get('username') or is_banned():
        flash('Login required!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        message_text = request.form.get('message', '').strip()
        if message_text:
            messages = load_messages()
            messages.append({
                'id': str(uuid.uuid4()),
                'username': session['username'],
                'role': session['role'],
                'message': message_text,
                'timestamp': datetime.now().isoformat()
            })
            save_messages(messages)
            flash('Message sent! ♥', 'success')
    
    messages = load_messages()
    users = load_users()
    settings = load_settings()
    custom_elements = load_custom_elements()
    
    messages_html = ''
    for msg in messages[-50:]:
        user_role = users.get(msg['username'], {}).get('role', 'guest')
        badge_class = f'badge-{user_role}'
        
        messages_html += f'''
            <div class="message">
                <div class="message-header">
                    <span oncontextmenu="showUserActions(event, '{msg['username']}', '{user_role}')" style="cursor: pointer;">
                        {msg['username']} <span class="user-badge {badge_class}">{user_role}</span>
                    </span>
                    <small>{datetime.fromisoformat(msg['timestamp']).strftime('%m/%d %H:%M')}</small>
                </div>
                <div>{msg['message']}</div>
            </div>
        '''
    
    content = f'''
        <div class="user-panel">
            <h2 class="rainbow-text">FC Message Channel ♥</h2>
            <div class="message-channel" id="messages-container">
                {messages_html}
            </div>
            <form method="POST" style="margin-top: 20px;">
                <div class="form-group">
                    <input type="text" name="message" placeholder="Type your message here... ♥" required>
                </div>
                <button type="submit">Send Message ♥</button>
            </form>
        </div>
    '''
    return render_template_string(HTML_TEMPLATE, settings=settings, content=content, session=session, custom_elements=custom_elements)

@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    if not session.get('username'):
        flash('Login required!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        suggestion_text = request.form.get('suggestion', '').strip()
        if suggestion_text:
            suggestions = load_suggestions()
            suggestions.append({
                'id': str(uuid.uuid4()),
                'username': session['username'],
                'suggestion': suggestion_text,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            })
            save_suggestions(suggestions)
            flash('Suggestion submitted! ♥', 'success')
    
    suggestions = load_suggestions()
    settings = load_settings()
    custom_elements = load_custom_elements()
    
    suggestions_html = ''
    for sugg in suggestions:
        status_color = {'pending': '#ffff00', 'approved': '#00ff00', 'rejected': '#ff0000'}.get(sugg.get('status', 'pending'), '#ffff00')
        suggestions_html += f'''
            <div class="suggestion-item">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <strong>{sugg['username']}</strong>
                    <span style="color: {status_color}; font-weight: bold;">{sugg.get('status', 'pending').upper()}</span>
                </div>
                <p>{sugg['suggestion']}</p>
                <small>{datetime.fromisoformat(sugg['timestamp']).strftime('%m/%d/%Y %H:%M')}</small>
                {f'<div style="margin-top: 10px;"><button onclick="updateSuggestion(\'{sugg["id"]}\', \'approved\')">Approve</button><button onclick="updateSuggestion(\'{sugg["id"]}\', \'rejected\')" class="btn-danger">Reject</button></div>' if is_admin() else ''}
            </div>
        '''
    
    content = f'''
        <div class="user-panel">
            <h2 class="rainbow-text">Site Suggestions ♥</h2>
            <form method="POST" style="margin-bottom: 30px;">
                <div class="form-group">
                    <label for="suggestion">Your Suggestion:</label>
                    <textarea id="suggestion" name="suggestion" placeholder="Tell us how we can improve the site! ♥" required></textarea>
                </div>
                <button type="submit">Submit Suggestion ♥</button>
            </form>
            
            <h3 class="rainbow-text">All Suggestions</h3>
            {suggestions_html if suggestions_html else '<p style="text-align: center; color: #ff69b4;">No suggestions yet! ♥</p>'}
        </div>
        
        <script>
            function updateSuggestion(id, status) {{
                fetch('/update-suggestion', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{id: id, status: status}})
                }}).then(() => location.reload());
            }}
        </script>
    '''
    return render_template_string(HTML_TEMPLATE, settings=settings, content=content, session=session, custom_elements=custom_elements)

@app.route('/update-suggestion', methods=['POST'])
def update_suggestion():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    suggestion_id = data.get('id')
    status = data.get('status')
    
    suggestions = load_suggestions()
    for sugg in suggestions:
        if sugg['id'] == suggestion_id:
            sugg['status'] = status
            break
    
    save_suggestions(suggestions)
    return jsonify({'success': True})

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('username') or not is_host_or_admin():
        flash('Access denied!', 'error')
        return redirect(url_for('home'))
    
    username = session['username']
    profiles = load_profiles()
    
    if request.method == 'POST':
        character_name = request.form.get('character_name', '').strip()
        character_bio = request.form.get('character_bio', '').strip()
        character_image = request.files.get('character_image')
        
        profile_data = profiles.get(username, {})
        profile_data['character_name'] = character_name
        profile_data['character_bio'] = character_bio
        
        if character_image and character_image.filename:
            image_data = base64.b64encode(character_image.read()).decode('utf-8')
            profile_data['character_image'] = f"data:image/{character_image.filename.split('.')[-1]};base64,{image_data}"
        
        profiles[username] = profile_data
        save_profiles(profiles)
        flash('Profile updated! ♥', 'success')
        return redirect(url_for('view_profile', username=username))
    
    user_profile = profiles.get(username, {})
    settings = load_settings()
    custom_elements = load_custom_elements()
    
    content = f'''
        <div class="user-panel">
            <h2 class="rainbow-text">My Character Profile ♥</h2>
            <form method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="character_name">Character Name:</label>
                    <input type="text" id="character_name" name="character_name" 
                           value="{user_profile.get('character_name', '')}" required>
                </div>
                <div class="form-group">
                    <label for="character_image">Character Image:</label>
                    <input type="file" id="character_image" name="character_image" accept="image/*">
                </div>
                <div class="form-group">
                    <label for="character_bio">Character Bio:</label>
                    <textarea id="character_bio" name="character_bio" required>{user_profile.get('character_bio', '')}</textarea>
                </div>
                <button type="submit">Save Profile ♥</button>
                <a href="/view-profile/{username}"><button type="button" class="btn-secondary">View My Profile ♥</button></a>
            </form>
        </div>
    '''
    return render_template_string(HTML_TEMPLATE, settings=settings, content=content, session=session, custom_elements=custom_elements)

@app.route('/view-profile/<username>')
def view_profile(username):
    profiles = load_profiles()
    users = load_users()
    
    if username not in profiles:
        flash('Profile not found!', 'error')
        return redirect(url_for('characters'))
    
    profile = profiles[username]
    user_role = users.get(username, {}).get('role', 'guest')
    is_owner = session.get('username') == username
    
    profile_messages = profile.get('messages', [])
    profile_screenshots = profile.get('screenshots', [])
    
    settings = load_settings()
    custom_elements = load_custom_elements()
    
    message_form = ''
    if is_owner:
        message_form = f'''
            <form method="POST" action="/profile-message/{username}">
                <div class="form-group">
                    <label>Add Private Note:</label>
                    <textarea name="message" placeholder="Private thoughts, notes, or updates... ♥"></textarea>
                </div>
                <button type="submit">Add Note ♥</button>
            </form>
        '''
    
    screenshot_form = ''
    if is_owner:
        screenshot_form = f'''
            <form method="POST" action="/profile-screenshot/{username}" enctype="multipart/form-data">
                <div class="form-group">
                    <label>Add Screenshot:</label>
                    <input type="file" name="screenshot" accept="image/*" required>
                </div>
                <div class="form-group">
                    <input type="text" name="caption" placeholder="Screenshot caption... ♥">
                </div>
                <button type="submit">Upload Screenshot ♥</button>
            </form>
        '''
    
    messages_html = ''
    for msg in profile_messages:
        delete_btn = ''
        if is_admin() or is_owner:
            delete_btn = f'<button class="btn-danger" onclick="deleteProfileMessage(\'{username}\', \'{msg["id"]}\')">Delete</button>'
        
        messages_html += f'''
            <div class="message">
                <div class="message-header">
                    <span>{msg.get("timestamp", "")}</span>
                    {delete_btn}
                </div>
                <div>{msg["message"]}</div>
            </div>
        '''
    
    screenshots_html = ''
    for screenshot in profile_screenshots:
        delete_btn = ''
        if is_admin() or is_owner:
            delete_btn = f'<button class="btn-danger" onclick="deleteProfileScreenshot(\'{username}\', \'{screenshot["id"]}\')">Delete</button>'
        
        screenshots_html += f'''
            <div style="position: relative; display: inline-block; margin: 10px;">
                <img src="{screenshot['data']}" class="profile-image" onclick="openImageModal(this.src)">
                <p style="text-align: center; margin-top: 5px;">{screenshot.get('caption', '')}</p>
                {delete_btn}
            </div>
        '''
    
    content = f'''
        <div class="profile-section">
            <h2 class="rainbow-text">{profile.get('character_name', username)}'s Profile ♥</h2>
            
            <div class="character-profile">
                {f'<img src="{profile["character_image"]}" class="character-image">' if profile.get('character_image') else '<div class="character-image" style="background: rgba(255,105,180,0.2); display: flex; align-items: center; justify-content: center;">No Image</div>'}
                <div class="character-info">
                    <h3>{profile.get('character_name', 'Unknown')} <span class="user-badge badge-{user_role}">{user_role}</span></h3>
                    <p><strong>Player:</strong> {username}</p>
                    <p><strong>Bio:</strong></p>
                    <p>{profile.get('character_bio', 'No bio available.')}</p>
                    
                    {f'<a href="/profile"><button>Edit Profile ♥</button></a>' if is_owner else ''}
                </div>
            </div>
            
            <div class="profile-section">
                <h3 class="rainbow-text">Screenshots ♥</h3>
                {screenshot_form}
                <div class="screenshot-grid">
                    {screenshots_html if screenshots_html else '<p>No screenshots yet! ♥</p>'}
                </div>
            </div>
            
            <div class="profile-section">
                <h3 class="rainbow-text">{'Private Notes' if is_owner else 'Recent Updates'} ♥</h3>
                {message_form}
                <div class="message-channel">
                    {messages_html if messages_html else '<p>No messages yet! ♥</p>'}
                </div>
            </div>
        </div>
        
        <div id="imageModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('imageModal')">&times;</span>
                <img id="modalImage" style="width: 100%; height: auto;">
            </div>
        </div>
        
        <script>
            function openImageModal(src) {{
                document.getElementById('modalImage').src = src;
                openModal('imageModal');
            }}
            
            function deleteProfileMessage(username, messageId) {{
                if (confirm('Delete this message?')) {{
                    fetch('/delete-profile-message', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{username: username, messageId: messageId}})
                    }}).then(() => location.reload());
                }}
            }}
            
            function deleteProfileScreenshot(username, screenshotId) {{
                if (confirm('Delete this screenshot?')) {{
                    fetch('/delete-profile-screenshot', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{username: username, screenshotId: screenshotId}})
                    }}).then(() => location.reload());
                }}
            }}
        </script>
    '''
    return render_template_string(HTML_TEMPLATE, settings=settings, content=content, session=session, custom_elements=custom_elements)

@app.route('/profile-message/<username>', methods=['POST'])
def profile_message(username):
    if session.get('username') != username:
        flash('Access denied!', 'error')
        return redirect(url_for('view_profile', username=username))
    
    message_text = request.form.get('message', '').strip()
    if message_text:
        profiles = load_profiles()
        if username not in profiles:
            profiles[username] = {}
        
        if 'messages' not in profiles[username]:
            profiles[username]['messages'] = []
        
        profiles[username]['messages'].append({
            'id': str(uuid.uuid4()),
            'message': message_text,
            'timestamp': datetime.now().strftime('%m/%d/%Y %H:%M')
        })
        
        save_profiles(profiles)
        flash('Note added! ♥', 'success')
    
    return redirect(url_for('view_profile', username=username))

@app.route('/profile-screenshot/<username>', methods=['POST'])
def profile_screenshot(username):
    if session.get('username') != username:
        flash('Access denied!', 'error')
        return redirect(url_for('view_profile', username=username))
    
    screenshot = request.files.get('screenshot')
    caption = request.form.get('caption', '').strip()
    
    if screenshot and screenshot.filename:
        image_data = base64.b64encode(screenshot.read()).decode('utf-8')
        data_url = f"data:image/{screenshot.filename.split('.')[-1]};base64,{image_data}"
        
        profiles = load_profiles()
        if username not in profiles:
            profiles[username] = {}
        
        if 'screenshots' not in profiles[username]:
            profiles[username]['screenshots'] = []
        
        profiles[username]['screenshots'].append({
            'id': str(uuid.uuid4()),
            'data': data_url,
            'caption': caption,
            'timestamp': datetime.now().strftime('%m/%d/%Y %H:%M')
        })
        
        save_profiles(profiles)
        flash('Screenshot uploaded! ♥', 'success')
    
    return redirect(url_for('view_profile', username=username))

@app.route('/delete-profile-message', methods=['POST'])
def delete_profile_message():
    data = request.get_json()
    username = data.get('username')
    message_id = data.get('messageId')
    
    if session.get('username') != username and not is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    profiles = load_profiles()
    if username in profiles and 'messages' in profiles[username]:
        profiles[username]['messages'] = [
            msg for msg in profiles[username]['messages'] 
            if msg['id'] != message_id
        ]
        save_profiles(profiles)
    
    return jsonify({'success': True})

@app.route('/delete-profile-screenshot', methods=['POST'])
def delete_profile_screenshot():
    data = request.get_json()
    username = data.get('username')
    screenshot_id = data.get('screenshotId')
    
    if session.get('username') != username and not is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    profiles = load_profiles()
    if username in profiles and 'screenshots' in profiles[username]:
        profiles[username]['screenshots'] = [
            screenshot for screenshot in profiles[username]['screenshots'] 
            if screenshot['id'] != screenshot_id
        ]
        save_profiles(profiles)
    
    return jsonify({'success': True})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not is_admin():
        flash('Admin access required!', 'error')
        return redirect(url_for('home'))
    
    settings = load_settings()
    custom_elements = load_custom_elements()
    
    if request.method == 'POST':
        form_data = request.form.to_dict()
        
        for key in ['site_title', 'fc_name', 'server', 'welcome_message', 'about_text', 'rainbow_speed', 'background_color', 'text_color']:
            if key in form_data:
                settings[key] = form_data[key]
        
        if 'music_volume' in form_data:
            settings['music_volume'] = float(form_data['music_volume'])
        if 'sound_volume' in form_data:
            settings['sound_volume'] = float(form_data['sound_volume'])
        
        if 'background_image' in request.files and request.files['background_image'].filename:
            bg_image = request.files['background_image']
            image_data = base64.b64encode(bg_image.read()).decode('utf-8')
            settings['background_image'] = image_data
        
        if 'background_video' in request.files and request.files['background_video'].filename:
            bg_video = request.files['background_video']
            video_data = base64.b64encode(bg_video.read()).decode('utf-8')
            settings['background_video'] = video_data
        
        if 'background_music' in request.files and request.files['background_music'].filename:
            bg_music = request.files['background_music']
            music_data = base64.b64encode(bg_music.read()).decode('utf-8')
            settings['background_music'] = music_data
        
        if 'click_sound' in request.files and request.files['click_sound'].filename:
            click_sound = request.files['click_sound']
            sound_data = base64.b64encode(click_sound.read()).decode('utf-8')
            settings['click_sound'] = sound_data
        
        save_settings(settings)
        flash('Settings updated successfully! ♥', 'success')
        return redirect(url_for('admin'))
    
    content = f'''
        <div class="admin-panel">
            <h2 class="rainbow-text">Admin Control Panel ♥</h2>
            
            <form method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="site_title">Site Title:</label>
                    <input type="text" id="site_title" name="site_title" value="{settings['site_title']}">
                </div>
                
                <div class="form-group">
                    <label for="fc_name">Free Company Name:</label>
                    <input type="text" id="fc_name" name="fc_name" value="{settings['fc_name']}">
                </div>
                
                <div class="form-group">
                    <label for="server">Server Name:</label>
                    <input type="text" id="server" name="server" value="{settings['server']}">
                </div>
                
                <div class="form-group">
                    <label for="welcome_message">Welcome Message:</label>
                    <textarea id="welcome_message" name="welcome_message">{settings['welcome_message']}</textarea>
                </div>
                
                <div class="form-group">
                    <label for="about_text">About Text:</label>
                    <textarea id="about_text" name="about_text">{settings['about_text']}</textarea>
                </div>
                
                <div class="form-group">
                    <label for="rainbow_speed">Rainbow Animation Speed:</label>
                    <select id="rainbow_speed" name="rainbow_speed">
                        <option value="1s" {"selected" if settings['rainbow_speed'] == "1s" else ""}>Fast (1s)</option>
                        <option value="3s" {"selected" if settings['rainbow_speed'] == "3s" else ""}>Normal (3s)</option>
                        <option value="5s" {"selected" if settings['rainbow_speed'] == "5s" else ""}>Slow (5s)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="background_color">Background Color:</label>
                    <input type="color" id="background_color" name="background_color" value="{settings['background_color']}">
                </div>
                
                <div class="form-group">
                    <label for="text_color">Text Color:</label>
                    <input type="color" id="text_color" name="text_color" value="{settings['text_color']}">
                </div>
                
                <div class="form-group">
                    <label for="background_image">Background Image:</label>
                    <input type="file" id="background_image" name="background_image" accept="image/*">
                    <small>Current: {"Set" if settings.get('background_image') else "None"}</small>
                </div>
                
                <div class="form-group">
                    <label for="background_video">Background Video:</label>
                    <input type="file" id="background_video" name="background_video" accept="video/*">
                    <small>Current: {"Set" if settings.get('background_video') else "None"}</small>
                </div>
                
                <div class="form-group">
                    <label for="background_music">Background Music:</label>
                    <input type="file" id="background_music" name="background_music" accept="audio/*">
                    <small>Current: {"Set" if settings.get('background_music') else "None"}</small>
                </div>
                
                <div class="form-group">
                    <label for="click_sound">Click Sound Effect:</label>
                    <input type="file" id="click_sound" name="click_sound" accept="audio/*">
                    <small>Current: {"Set" if settings.get('click_sound') else "None"}</small>
                </div>
                
                <div class="form-group">
                    <label for="music_volume">Music Volume:</label>
                    <input type="range" id="music_volume" name="music_volume" min="0" max="1" step="0.1" value="{settings['music_volume']}">
                    <span id="music_volume_display">{int(settings['music_volume'] * 100)}%</span>
                </div>
                
                <div class="form-group">
                    <label for="sound_volume">Sound Effects Volume:</label>
                    <input type="range" id="sound_volume" name="sound_volume" min="0" max="1" step="0.1" value="{settings['sound_volume']}">
                    <span id="sound_volume_display">{int(settings['sound_volume'] * 100)}%</span>
                </div>
                
                <button type="submit">Save Settings ♥</button>
            </form>
            
            <div style="margin-top: 30px;">
                <h3 class="rainbow-text">Quick Actions</h3>
                <button onclick="clearMedia('background_image')" class="btn-danger">Clear Background Image</button>
                <button onclick="clearMedia('background_video')" class="btn-danger">Clear Background Video</button>
                <button onclick="clearMedia('background_music')" class="btn-danger">Clear Background Music</button>
                <button onclick="clearMedia('click_sound')" class="btn-danger">Clear Click Sound</button>
            </div>
        </div>
        
        <script>
            document.getElementById('music_volume').addEventListener('input', function() {{
                document.getElementById('music_volume_display').textContent = Math.round(this.value * 100) + '%';
            }});
            
            document.getElementById('sound_volume').addEventListener('input', function() {{
                document.getElementById('sound_volume_display').textContent = Math.round(this.value * 100) + '%';
            }});
            
            function clearMedia(mediaType) {{
                if (confirm('Are you sure you want to clear this media?')) {{
                    fetch('/clear-media', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{mediaType: mediaType}})
                    }}).then(() => location.reload());
                }}
            }}
        </script>
    '''
    
    return render_template_string(HTML_TEMPLATE, settings=settings, content=content, session=session, custom_elements=custom_elements)

@app.route('/manage-users')
def manage_users():
    if not is_admin():
        flash('Admin access required!', 'error')
        return redirect(url_for('home'))
    
    users = load_users()
    profiles = load_profiles()
    settings = load_settings()
    custom_elements = load_custom_elements()
    
    users_html = ''
    for username, user_data in users.items():
        profile = profiles.get(username, {})
        banned_status = '❌ BANNED' if user_data.get('banned', False) else '✅ Active'
        banned_class = 'badge-danger' if user_data.get('banned', False) else 'badge-success'
        
        users_html += f'''
            <div class="user-card">
                <h4>{username}</h4>
                <p><strong>Role:</strong> <span class="user-badge badge-{user_data.get('role', 'guest')}">{user_data.get('role', 'guest')}</span></p>
                <p><strong>Status:</strong> <span class="user-badge {banned_class}">{banned_status}</span></p>
                <p><strong>Character:</strong> {profile.get('character_name', 'Not set')}</p>
                <p><strong>Joined:</strong> {datetime.fromisoformat(user_data.get('created_at', datetime.now().isoformat())).strftime('%m/%d/%Y')}</p>
                
                <div style="margin-top: 15px;">
                    {f'<button onclick="viewProfile(\'{username}\')">View Profile</button>' if profile.get('character_name') else ''}
                    
                    {f'<button onclick="changeRole(\'{username}\', \'admin\')" class="btn-success">Make Admin</button>' if user_data.get('role') != 'admin' else ''}
                    {f'<button onclick="changeRole(\'{username}\', \'host\')" class="btn-secondary">Make Host</button>' if user_data.get('role') != 'host' else ''}
                    {f'<button onclick="changeRole(\'{username}\', \'guest\')" class="btn-secondary">Make Guest</button>' if user_data.get('role') != 'guest' else ''}
                    
                    {f'<button onclick="unbanUser(\'{username}\')" class="btn-success">Unban</button>' if user_data.get('banned', False) else f'<button onclick="banUser(\'{username}\')" class="btn-danger">Ban</button>' if username != session.get('username') else ''}
                    
                    {f'<button onclick="deleteUser(\'{username}\')" class="btn-danger">Delete User</button>' if username != session.get('username') else ''}
                </div>
            </div>
        '''
    
    content = f'''
        <div class="admin-panel">
            <h2 class="rainbow-text">User Management ♥</h2>
            
            <div style="margin-bottom: 20px;">
                <h3>User Statistics</h3>
                <p><strong>Total Users:</strong> {len(users)}</p>
                <p><strong>Admins:</strong> {len([u for u in users.values() if u.get('role') == 'admin'])}</p>
                <p><strong>Hosts:</strong> {len([u for u in users.values() if u.get('role') == 'host'])}</p>
                <p><strong>Guests:</strong> {len([u for u in users.values() if u.get('role') == 'guest'])}</p>
                <p><strong>Banned:</strong> {len([u for u in users.values() if u.get('banned', False)])}</p>
            </div>
            
            <div class="users-grid">
                {users_html}
            </div>
        </div>
        
        <script>
            function deleteUser(username) {{
                if (confirm(`Are you sure you want to permanently delete user ${{username}}? This cannot be undone!`)) {{
                    fetch('/delete-user', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{username: username}})
                    }}).then(() => location.reload());
                }}
            }}
            
            function unbanUser(username) {{
                fetch('/unban-user', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{username: username}})
                }}).then(() => location.reload());
            }}
        </script>
    '''
    
    return render_template_string(HTML_TEMPLATE, settings=settings, content=content, session=session, custom_elements=custom_elements)

@app.route('/clear-media', methods=['POST'])
def clear_media():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    media_type = data.get('mediaType')
    
    settings = load_settings()
    if media_type in settings:
        settings[media_type] = ''
        save_settings(settings)
    
    return jsonify({'success': True})

@app.route('/ban-user', methods=['POST'])
def ban_user():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    username = data.get('username')
    
    users = load_users()
    if username in users and username != session.get('username'):
        users[username]['banned'] = True
        save_users(users)
        return jsonify({'success': True})
    
    return jsonify({'error': 'Cannot ban this user'}), 400

@app.route('/unban-user', methods=['POST'])
def unban_user():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    username = data.get('username')
    
    users = load_users()
    if username in users:
        users[username]['banned'] = False
        save_users(users)
        return jsonify({'success': True})
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/change-role', methods=['POST'])
def change_role():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    username = data.get('username')
    role = data.get('role')
    
    if role not in ['admin', 'host', 'guest']:
        return jsonify({'error': 'Invalid role'}), 400
    
    users = load_users()
    if username in users and username != session.get('username'):
        users[username]['role'] = role
        save_users(users)
        return jsonify({'success': True})
    
    return jsonify({'error': 'Cannot change role for this user'}), 400

@app.route('/delete-user', methods=['POST'])
def delete_user():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    username = data.get('username')
    
    if username == session.get('username'):
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        
        profiles = load_profiles()
        if username in profiles:
            del profiles[username]
            save_profiles(profiles)
        
        return jsonify({'success': True})
    
    return jsonify({'error': 'User not found'}), 404

# NEW ADVANCED EDIT MODE ROUTES

@app.route('/save-element-layer', methods=['POST'])
def save_element_layer():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        element_id = data.get('elementId')
        layer = data.get('layer')
        
        layers_file = os.path.join(SCRIPT_DIR, 'element_layers.json')
        layers = load_json_file(layers_file, {})
        
        layers[element_id] = layer
        save_json_file(layers_file, layers)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/get-element-layers')
def get_element_layers():
    layers_file = os.path.join(SCRIPT_DIR, 'element_layers.json')
    layers = load_json_file(layers_file, {})
    return jsonify(layers)

@app.route('/get-all-elements')
def get_all_elements():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    all_elements = {}
    
    # Get sections from all pages
    page_suffixes = ['', '_characters', '_messages', '_suggestions', '_profile', '_admin', '_manage-users']
    page_names = ['/', '/characters', '/messages', '/suggestions', '/profile', '/admin', '/manage-users']
    
    for i, suffix in enumerate(page_suffixes):
        sections_file = os.path.join(SCRIPT_DIR, f'site_sections{suffix}.json')
        sections = load_json_file(sections_file, {})
        
        page_elements = []
        for section_id, section in sections.items():
            for content_item in section.get('content', []):
                page_elements.append({
                    'id': f'section-{section_id}',
                    'type': content_item.get('type', 'unknown'),
                    'section_title': section.get('title', 'Unnamed Section')
                })
        
        all_elements[page_names[i]] = page_elements
    
    # Add custom elements
    custom_elements = load_custom_elements()
    for element in custom_elements:
        page = element.get('page', '/')
        if page not in all_elements:
            all_elements[page] = []
        all_elements[page].append({
            'id': f'custom-{element["id"]}',
            'type': element.get('type', 'custom'),
            'content': element.get('content', '')[:50] + '...' if len(element.get('content', '')) > 50 else element.get('content', '')
        })
    
    return jsonify(all_elements)

@app.route('/save-cross-page-element', methods=['POST'])
def save_cross_page_element():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        element_id = data.get('elementId')
        element_data = data.get('elementData')
        page = data.get('page')
        
        # Save element data to cross-page elements file
        cross_page_file = os.path.join(SCRIPT_DIR, 'cross_page_elements.json')
        cross_page_elements = load_json_file(cross_page_file, {})
        
        if page not in cross_page_elements:
            cross_page_elements[page] = {}
        
        cross_page_elements[page][element_id] = element_data
        save_json_file(cross_page_file, cross_page_elements)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/delete-cross-page-element', methods=['POST'])
def delete_cross_page_element():
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        element_id = data.get('elementId')
        page = data.get('page')
        
        # Delete from sections if it's a section element
        if element_id.startswith('section-'):
            section_id = element_id.replace('section-', '')
            page_suffix = ''
            if page == '/characters':
                page_suffix = '_characters'
            elif page == '/messages':
                page_suffix = '_messages'
            elif page == '/suggestions':
                page_suffix = '_suggestions'
            elif page == '/profile':
                page_suffix = '_profile'
            elif page == '/admin':
                page_suffix = '_admin'
            elif page == '/manage-users':
                page_suffix = '_manage-users'
            
            sections_file = os.path.join(SCRIPT_DIR, f'site_sections{page_suffix}.json')
            sections = load_json_file(sections_file, {})
            
            if section_id in sections:
                del sections[section_id]
                save_json_file(sections_file, sections)
        
        # Delete from custom elements if it's a custom element
        elif element_id.startswith('custom-'):
            elements = load_custom_elements()
            element_uuid = element_id.replace('custom-', '')
            elements = [el for el in elements if el['id'] != element_uuid]
            save_custom_elements(elements)
        
        # Delete from cross-page elements
        cross_page_file = os.path.join(SCRIPT_DIR, 'cross_page_elements.json')
        cross_page_elements = load_json_file(cross_page_file, {})
        
        if page in cross_page_elements and element_id in cross_page_elements[page]:
            del cross_page_elements[page][element_id]
            save_json_file(cross_page_file, cross_page_elements)
        
        # Delete from transforms
        transforms_file = os.path.join(SCRIPT_DIR, 'element_transforms.json')
        transforms = load_json_file(transforms_file, {})
        if element_id in transforms:
            del transforms[element_id]
            save_json_file(transforms_file, transforms)
        
        # Delete from layers
        layers_file = os.path.join(SCRIPT_DIR, 'element_layers.json')
        layers = load_json_file(layers_file, {})
        if element_id in layers:
            del layers[element_id]
            save_json_file(layers_file, layers)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Initialize files and run
if __name__ == '__main__':
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
    if not os.path.exists(USERS_FILE):
        save_users(DEFAULT_USERS)
    if not os.path.exists(os.path.join(SCRIPT_DIR, 'site_sections.json')):
        save_json_file(os.path.join(SCRIPT_DIR, 'site_sections.json'), {})
    
    for page_suffix in ['_characters', '_messages', '_suggestions', '_profile', '_admin', '_manage-users']:
        sections_file = os.path.join(SCRIPT_DIR, f'site_sections{page_suffix}.json')
        if not os.path.exists(sections_file):
            save_json_file(sections_file, {})
    
    if not os.path.exists(os.path.join(SCRIPT_DIR, 'element_transforms.json')):
        save_json_file(os.path.join(SCRIPT_DIR, 'element_transforms.json'), {})
    
    # Initialize new advanced edit mode files
    if not os.path.exists(os.path.join(SCRIPT_DIR, 'element_layers.json')):
        save_json_file(os.path.join(SCRIPT_DIR, 'element_layers.json'), {})
    
    if not os.path.exists(os.path.join(SCRIPT_DIR, 'cross_page_elements.json')):
        save_json_file(os.path.join(SCRIPT_DIR, 'cross_page_elements.json'), {})
    
    print("🏳️‍🌈 Starting The Ultimate Gay Agenda FFXIV FC Server! ♥")
    print("Default admin login: admin / admin123")
    print("Server will be available at: http://localhost:5000")
    print("\n✨ ULTIMATE FEATURES:")
    print("♥ PERSISTENT MUSIC - Continues across pages!")
    print("♥ ADVANCED EDIT MODE - Full control over all elements!")
    print("♥ 5-LAYER SYSTEM - Front to back z-index control!")
    print("♥ FONT CUSTOMIZATION - 17+ fonts, weights, effects!")
    print("♥ SMART TEXT RESIZE - Font scales with container!")
    print("♥ ENHANCED RIGHT-CLICK - Edit/Copy/Layer controls!")
    print("♥ CROSS-PAGE MANAGEMENT - Edit elements from any page!")
    print("♥ TRANSPARENT MODE - Perfect for overlays!")
    print("♥ DISCORD EMBEDS - Add your server widget!")
    print("♥ ELEMENT MANAGER - View and manage all site elements!")
    print("♥ LAYER MANAGER - Visual layer control panel!")
    print("\n🎮 Perfect for FFXIV Free Companies! 🏳️‍🌈")
    print("\n🎨 EDIT MODE FEATURES:")
    print("📚 Layer System: 5 = Front, 1 = Back")
    print("✏️ Inline Editing: Right-click any element")
    print("📋 Copy Elements: Duplicate with offset")
    print("🎯 Smart Transforms: Text resizes properly")
    print("🗂️ Cross-Page Management: Edit from anywhere")
    print("⌨️ Keyboard Shortcuts: Ctrl+G, Delete, Escape")
    
    app.run(debug=True, host='0.0.0.0', port=5000)