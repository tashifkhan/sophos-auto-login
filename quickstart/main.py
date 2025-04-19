from flask import Flask, render_template_string, url_for
import socket
import webbrowser
import threading
import time

app = Flask(__name__)

@app.route('/')
def documentation():
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sophos Auto Login - Quickstart Guide</title>
            <link rel="icon" href="data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg' version='1.1'%3E%3Cpath style='fill:%23ffffff;stroke:none;' d='m 65,3 0,19 19,0 z'/%3E%3Cpath style='fill:%23EBEBDA;stroke:%23777777;stroke-width:2;' d='m 65,3 0,19 19,0 0,74 -72,0 0,-93 53,0 19,19'/%3E%3Cg style='fill:%23386DA1;'%3E%3Cpath d = 'm 38 65 l -3 0 a 5 10 0 0 1 0,-20 l 15,0 l 0,-3 l -10,0 l 0,-6 a 9 5 0 0 1 18,0 l 0,14 a 3,3 0 0 1 -3,3 l -12,0 a 5,5 0 0 0 -5,5 z'/%3E%3Cellipse style='fill:%23ffffff;' rx='2' ry='2' cx='46' cy='38' /%3E%3C/g%3E%3Cg style='fill:%23FFC83A;'%3E%3Cpath d = 'm 61 45 l 0,6 a 5,5 0 0 1 -5,5 l -12,0 a 3,3 0 0 0 -3,3 l 0,14 a 9,5 0 0 0 18,0 l 0,-6 l -10,0  l 0,-3 l 15,0 a 5 10 0 0 0 0,-20 l -3 0 z' /%3E%3Cellipse style='fill:%23ffffff;' rx='2' ry='2' cx='53' cy='71' /%3E%3C/g%3E%3C/svg%3E" type="image/svg+xml">
            <style>
                :root {
                    --primary-color: #e4e4e4;
                    --secondary-color: #64ffda;
                    --background-color: #0a192f;
                    --code-background: #112240;
                    --text-color: #8892b0;
                    --heading-color: #ccd6f6;
                    --card-background: #112240;
                    --hover-color: #233554;
                    --sidebar-width: 280px;
                    --header-height: 60px;
                    --line-highlight: rgba(100, 255, 218, 0.1);
                    --token-comment: #6c7693;
                    --token-keyword: #ff79c6;
                    --token-string: #a5e844;
                    --token-number: #bd93f9;
                    --token-function: #ffb86c;
                    --token-operator: #f8f8f2;
                    --token-class: #8be9fd;
                    --token-variable: #f8f8f2;
                    --border-color: #233554;
                }
                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }
                body {
                    font-family: 'SF Mono', 'Fira Code', 'Monaco', monospace;
                    line-height: 1.6;
                    color: var(--text-color);
                    margin: 0;
                    background: var(--background-color);
                    transition: all 0.25s ease-in-out;
                    display: flex;
                    flex-direction: column;
                    min-height: 100vh;
                }
                a {
                    color: var(--secondary-color);
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                h1, h2, h3 {
                    color: var(--heading-color);
                    margin-top: 2.5rem;
                    margin-bottom: 1rem;
                    font-weight: 600;
                    letter-spacing: -0.5px;
                }
                h1 {
                    font-size: clamp(1.8rem, 4vw, 2.5rem);
                    margin-bottom: 2rem;
                    padding-bottom: 1rem;
                    border-bottom: 2px solid var(--secondary-color);
                }
                h3 {
                    margin-top: 1.75rem;
                    margin-bottom: 0.75rem;
                    font-size: 1.1rem;
                }
                .header {
                    height: var(--header-height);
                    background-color: var(--background-color);
                    border-bottom: 1px solid var(--hover-color);
                    display: flex;
                    align-items: center;
                    padding: 0 1.5rem;
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    z-index: 10;
                }
                .header h1 {
                    font-size: 1.25rem;
                    margin: 0;
                    padding: 0;
                    border: none;
                }
                .menu-toggle {
                    display: none;
                    font-size: 1.5rem;
                    border: none;
                    background: none;
                    color: var(--heading-color);
                    cursor: pointer;
                    margin-right: 1rem;
                }
                .header-logo {
                    font-weight: bold;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem; /* Add gap between logo and text */
                }
                .header-logo svg {
                    width: 30px; /* Adjust size as needed */
                    height: 30px;
                }
                .header-logo span {
                    color: var(--secondary-color);
                }
                .container {
                    display: flex;
                    flex: 1;
                    margin-top: var(--header-height);
                }
                .sidebar {
                    width: var(--sidebar-width);
                    background-color: var(--card-background);
                    border-right: 1px solid var(--hover-color);
                    height: calc(100vh - var(--header-height));
                    position: fixed;
                    overflow-y: auto;
                    scrollbar-width: thin;
                    scrollbar-color: var(--hover-color) var(--card-background);
                }
                .sidebar::-webkit-scrollbar {
                    width: 6px;
                }
                .sidebar::-webkit-scrollbar-track {
                    background: var(--card-background);
                }
                .sidebar::-webkit-scrollbar-thumb {
                    background-color: var(--hover-color);
                    border-radius: 3px;
                }
                .nav-section {
                    margin: 1rem 0;
                }
                .nav-section-title {
                    padding: 0.75rem 1.5rem;
                    font-weight: bold;
                    color: var(--heading-color);
                    text-transform: uppercase;
                    font-size: 0.85rem;
                    letter-spacing: 1px;
                    border-bottom: 1px solid var(--border-color);
                    margin-bottom: 0.5rem;
                }
                .nav-items {
                    list-style: none;
                    padding: 0;
                }
                .nav-item {
                    padding: 0.5rem 1.5rem 0.5rem 2rem;
                    border-left: 3px solid transparent;
                    transition: all 0.2s ease;
                }
                .nav-item:hover {
                    background-color: var(--hover-color);
                    border-left-color: var(--secondary-color);
                }
                .nav-item.active {
                    border-left-color: var(--secondary-color);
                    background-color: var(--hover-color);
                }
                .nav-link {
                    color: var(--text-color);
                    text-decoration: none;
                    display: block;
                    font-size: 0.9rem;
                }
                .nav-item.active .nav-link {
                    color: var(--heading-color);
                }
                .main-content {
                    flex: 1;
                    margin-left: var(--sidebar-width);
                    padding: 2rem;
                    max-width: calc(100% - var(--sidebar-width));
                }
                .content-section {
                    max-width: 900px;
                    margin: 0 auto;
                    padding-bottom: 3rem;
                }
                .section {
                    background: var(--card-background);
                    border-radius: 12px;
                    padding: 1.5rem 2rem;
                    margin: 1.5rem 0;
                    margin-bottom: 2.5rem;
                    box-shadow: 0 10px 30px -15px rgba(2,12,27,0.7);
                    border: 1px solid var(--border-color);
                    transition: all 0.2s ease-in-out;
                }
                .section h2 {
                    border-bottom: 1px solid var(--border-color);
                    padding-bottom: 1rem;
                    margin-top: 0;
                    margin-bottom: 1.5rem;
                    padding-top: 0.5rem;
                }
                p {
                    margin-bottom: 1rem;
                }
                code {
                    background: var(--code-background);
                    color: var(--secondary-color);
                    padding: 0.3rem 0.6rem;
                    border-radius: 6px;
                    font-family: 'SF Mono', 'Fira Code', monospace;
                    font-size: 0.85em;
                    word-break: break-word;
                    white-space: pre-wrap;
                }
                pre {
                    background: var(--code-background);
                    padding: 1.5rem;
                    border-radius: 12px;
                    overflow-x: auto;
                    margin: 1.5rem 0;
                    border: 1px solid var(--hover-color);
                    position: relative;
                }
                pre code {
                    padding: 0;
                    background: none;
                    color: var(--primary-color);
                    font-size: 0.9em;
                }
                .feature {
                    margin: 1.5rem 0;
                    padding: 1.25rem;
                    background: var(--hover-color);
                    border-radius: 8px;
                    box-shadow: 0 4px 12px -6px rgba(2,12,27,0.4);
                    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                    border-left: 4px solid var(--secondary-color);
                    padding-left: 1.75rem;
                }
                /* Added style for feature titles */
                .feature strong {
                    color: var(--heading-color); /* Use heading color for emphasis */
                    display: block; /* Make it a block element */
                    margin-bottom: 0.25rem; /* Add a little space below the title */
                }
                .feature:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px -6px rgba(2,12,27,0.5);
                }
                .note {
                    background: var(--hover-color);
                    padding: 1.25rem;
                    margin: 1.5rem 0;
                    border-radius: 8px;
                    border-left: 4px solid var(--token-function);
                    padding-left: 1.75rem;
                }
                .command {
                    margin: 1rem 0;
                    display: flex;
                    flex-wrap: wrap;
                    align-items: center;
                    padding: 1rem;
                    border: 1px solid var(--border-color);
                    border-radius: 8px;
                    background-color: rgba(0,0,0,0.1);
                }
                .command code {
                    margin-right: 1rem;
                    flex-shrink: 0;
                    margin-bottom: 0.5rem;
                }
                .command-desc {
                    margin-top: 0;
                    width: 100%;
                    font-size: 0.9em;
                    padding-top: 0.5rem;
                    border-top: 1px dashed var(--border-color);
                    margin-top: 0.75rem;
                }
                .download-btn {
                    display: inline-block;
                    background: var(--secondary-color);
                    color: var(--background-color);
                    padding: 0.75rem 1.5rem;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: bold;
                    margin: 1rem 0;
                    transition: all 0.2s ease;
                }
                .download-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px -6px rgba(2,12,27,0.5);
                }
                ul {
                    padding-left: 1.5rem;
                }
                li {
                    margin-bottom: 0.5rem;
                }
                .section ol, .section ul {
                    padding-left: 2rem;
                    margin-top: 0.75rem;
                }
                .section li {
                    margin-bottom: 0.75rem;
                }
                .section ul ul, .section ol ul {
                    margin-top: 0.5rem;
                    padding-left: 1.5rem;
                }
                footer {
                    margin-top: 3rem;
                    padding: 1.5rem;
                    border-top: 1px solid var(--hover-color);
                    text-align: center;
                    color: var(--text-color);
                    font-size: 0.9em;
                }
                /* Added style for footer developer link */
                .footer-dev {
                    display: block; /* Put on a new line */
                    margin-top: 0.5rem; /* Add some space above */
                    font-size: 0.85em; /* Slightly smaller */
                    color: var(--text-color); /* Match text color */
                }
                .footer-dev a {
                    color: var(--secondary-color); /* Keep link color */
                }
                @media (max-width: 1024px) {
                    .sidebar {
                        left: -280px;
                        transition: left 0.3s ease;
                        z-index: 20; /* Ensure sidebar is above overlay */
                    }
                    .sidebar.open {
                        left: 0;
                    }
                    .main-content {
                        margin-left: 0;
                        max-width: 100%;
                    }
                    .menu-toggle {
                        display: block;
                    }
                    .overlay {
                        display: none;
                        position: fixed;
                        top: var(--header-height);
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: rgba(0, 0, 0, 0.5);
                        z-index: 5; /* Lower z-index than sidebar */
                    }
                    .overlay.active {
                        display: block;
                    }
                }
                @media (max-width: 768px) {
                    .main-content {
                        padding: 1.5rem 1rem;
                    }
                    .section {
                        padding: 1.25rem;
                    }
                    pre {
                        padding: 1rem;
                        font-size: 0.9em;
                    }
                    code {
                        font-size: 0.8em;
                    }
                }
                @media (max-width: 480px) {
                    .main-content {
                        padding: 1rem 0.5rem;
                    }
                    .section {
                        padding: 1rem;
                    }
                    h1 {
                        font-size: 1.8rem;
                    }
                    pre {
                        padding: 0.75rem;
                        font-size: 0.85em;
                    }
                    .feature, .note {
                        padding: 1rem;
                        margin: 1rem 0;
                    }
                }
                [id] {
                    scroll-margin-top: calc(var(--header-height) + 1rem);
                }
                ::selection {
                    background: var(--secondary-color);
                    color: var(--background-color);
                }
                .token.comment,
                .token.prolog,
                .token.doctype,
                .token.cdata {
                    color: var(--token-comment);
                }
                .token.punctuation {
                    color: var(--token-operator);
                }
                .token.namespace {
                    opacity: 0.7;
                }
                .token.property,
                .token.tag,
                .token.constant,
                .token.symbol,
                .token.deleted {
                    color: var(--token-keyword);
                }
                .token.boolean,
                .token.number {
                    color: var(--token-number);
                }
                .token.selector,
                .token.attr-name,
                .token.string,
                .token.char,
                .token.builtin,
                .token.inserted {
                    color: var(--token-string);
                }
                .token.operator,
                .token.entity,
                .token.url,
                .language-css .token.string,
                .style .token.string {
                    color: var(--token-operator);
                }
                .token.atrule,
                .token.attr-value,
                .token.keyword {
                    color: var(--token-keyword);
                }
                .token.function,
                .token.class-name {
                    color: var(--token-function);
                }
                .token.regex,
                .token.important,
                .token.variable {
                    color: var(--token-variable);
                }
                .token.important,
                .token.bold {
                    font-weight: bold;
                }
                .token.italic {
                    font-style: italic;
                }
                .token.entity {
                    cursor: help;
                }
                pre.line-numbers {
                    position: relative;
                    padding-left: 3.8em;
                    counter-reset: linenumber;
                }
                pre.line-numbers > code {
                    position: relative;
                    white-space: inherit;
                }
                .line-numbers .line-numbers-rows {
                    position: absolute;
                    pointer-events: none;
                    top: 0;
                    font-size: 100%;
                    left: -3.8em;
                    width: 3em;
                    letter-spacing: -1px;
                    border-right: 1px solid #999;
                    user-select: none;
                }
                .line-numbers-rows > span {
                    display: block;
                    counter-increment: linenumber;
                }
                .line-numbers-rows > span:before {
                    content: counter(linenumber);
                    color: #999;
                    display: block;
                    padding-right: 0.8em;
                    text-align: right;
                }
                .line-highlight {
                    position: absolute;
                    left: 0;
                    right: 0;
                    padding-right: inherit;
                    background: var(--line-highlight);
                }
                pre .copy-button {
                    position: absolute;
                    top: 0.5rem;
                    right: 0.5rem;
                    padding: 0.3rem 0.6rem;
                    font-size: 0.8em;
                    background: var(--hover-color);
                    border: 1px solid var(--token-operator);
                    border-radius: 4px;
                    color: var(--token-operator);
                    cursor: pointer;
                    transition: all 0.2s ease;
                    opacity: 0;
                }
                pre:hover .copy-button {
                    opacity: 1;
                }
                pre .copy-button:hover {
                    background: var(--secondary-color);
                    color: var(--background-color);
                }
                .copied-message {
                    position: absolute;
                    top: 0.5rem;
                    right: 0.5rem;
                    padding: 0.3rem 0.6rem;
                    font-size: 0.8em;
                    background: var(--secondary-color);
                    color: var(--background-color);
                    border-radius: 4px;
                    pointer-events: none;
                    opacity: 0;
                    transition: opacity 0.2s ease;
                }
                .copied-message.show {
                    opacity: 1;
                }
            </style>
            <link rel="preconnect" href="https://cdnjs.cloudflare.com">
        </head>
        <body>
            <header class="header">
                <button class="menu-toggle" id="menuToggle">☰</button>
                <div class="header-logo">
                    <h1>Sophos<span> Auto Login</span></h1>
                </div>
            </header>
            
            <div class="container">
                <div class="sidebar" id="sidebar">
                    <nav>
                        <div class="nav-section">
                            <div class="nav-section-title">Getting Started</div>
                            <ul class="nav-items">
                                <li class="nav-item active"><a href="#introduction" class="nav-link">Introduction</a></li>
                                <li class="nav-item"><a href="#features" class="nav-link">Features</a></li>
                                <li class="nav-item"><a href="#quick-start" class="nav-link">Quick Start</a></li>
                            </ul>
                        </div>
                        
                        <div class="nav-section">
                            <div class="nav-section-title">Usage</div>
                            <ul class="nav-items">
                                <li class="nav-item"><a href="#command-line" class="nav-link">Command-Line Options</a></li>
                                <li class="nav-item"><a href="#interactive-menu" class="nav-link">Interactive Menu</a></li>
                                <li class="nav-item"><a href="#daemon-mode" class="nav-link">Daemon Mode</a></li>
                                <li class="nav-item"><a href="#screenshots" class="nav-link">Screenshots</a></li>
                            </ul>
                        </div>
                        
                        <div class="nav-section">
                            <div class="nav-section-title">Advanced</div>
                            <ul class="nav-items">
                                <li class="nav-item"><a href="#additional-features" class="nav-link">Additional Features</a></li>
                                <li class="nav-item"><a href="#creating-executable" class="nav-link">Creating Executable</a></li>
                                <li class="nav-item"><a href="#macos-linux-setup" class="nav-link">macOS and Linux Setup</a></li>
                            </ul>
                        </div>
                        
                        <div class="nav-section">
                            <div class="nav-section-title">Resources</div>
                            <ul class="nav-items">
                                <li class="nav-item"><a href="https://github.com/tashifkhan/sophos-auto-login" class="nav-link">GitHub Repository</a></li>
                                <li class="nav-item"><a href="https://github.com/tashifkhan/sophos-auto-login/releases" class="nav-link">Download Releases</a></li>
                            </ul>
                        </div>
                    </nav>
                </div>
                
                <div class="overlay" id="overlay"></div>
                
                <div class="main-content">
                    <div class="content-section">
                        <section id="introduction">
                            <h1>Sophos Automatic Login & Authentication</h1>
                            
                            <p>This Python script automates the login process for a Sophos internet web authentication portal. It ensures uninterrupted connectivity by automatically re-authenticating you every 2 minutes to prevent logout.</p>

                            <a href="https://github.com/tashifkhan/sophos-auto-login/releases" target="_blank" class="download-btn">Download Latest Release</a>
                        </section>

                        <section id="features" class="section">
                            <h2>Features</h2>
                            
                            <div class="feature">
                                <strong>SQLite Integration</strong>Credentials are securely stored in an SQLite database.
                            </div>
                            <div class="feature">
                                <strong>Automatic ID Switching</strong>Automatically switches to the next available ID if the current one fails or reaches its data limit.
                            </div>
                            <div class="feature">
                                <strong>Command-Line Arguments</strong>Supports various system arguments for automation and management.
                            </div>
                            <div class="feature">
                                <strong>Credential Management</strong>Add, edit, delete, import, and export credentials.
                            </div>
                            <div class="feature">
                                <strong>Interactive Menu</strong>User-friendly menu for managing credentials and starting the auto-login process.
                            </div>
                            <div class="feature">
                                <strong>CSV Import/Export</strong>Easily import/export credentials to/from a CSV file.
                            </div>
                            <div class="feature">
                                <strong>Auto-Logout Handling</strong>Ensures seamless reconnection by automatically logging in when disconnected.
                            </div>
                            <div class="feature">
                                <strong>Cross-Platform Compatibility</strong>Works on both Windows and Unix-based systems.
                            </div>
                            <div class="feature">
                                <strong>Daemon Mode</strong>Run the auto-login process in the background (Unix-like systems only).
                            </div>
                            <div class="feature">
                                <strong>Connection Check</strong>Periodically checks for internet connectivity and logs in if disconnected.
                            </div>
                            <div class="feature">
                                <strong>Scheduled Re-login</strong>Performs a scheduled re-login every 30 minutes to maintain connection.
                            </div>
                        </section>

                        <section id="quick-start" class="section">
                            <h2>Quick Start</h2>
                            
                            <h3>Using Pre-built Executable</h3>
                            <p>You can download the latest pre-built executable from the <a href="https://github.com/tashifkhan/sophos-auto-login/releases">Releases</a> section without installing Python or any dependencies:</p>
                            
                            <ol>
                                <li>Go to the Releases section on GitHub</li>
                                <li>Download the executable for your operating system (Windows, macOS, or Linux)</li>
                                <li>Run the downloaded file:
                                    <ul>
                                        <li><strong>Windows</strong>: Double-click the <code>autologin_script.exe</code> file</li>
                                        <li><strong>macOS</strong>:
                                            <ul>
                                                <li>Extract the downloaded autologin_script-mac.zip file</li>
                                                <li>Option 1: Remove the quarantine attribute by opening Terminal, navigating to the extraction location, and running <code>xattr -d com.apple.quarantine autologin_script</code> before executing it</li>
                                                <li>Option 2: Right-click on the extracted file, select "Open" from the context menu, then confirm the security dialog</li>
                                            </ul>
                                        </li>
                                        <li><strong>Linux</strong>:
                                            <ul>
                                                <li>Extract the downloaded autologin_script-linux.zip file</li>
                                                <li>Open Terminal, navigate to the extraction location and run <code>./autologin_script</code></li>
                                            </ul>
                                        </li>
                                    </ul>
                                </li>
                            </ol>

                            <h3>Building from Source</h3>
                            <p>If you prefer to run the Python script directly:</p>
                            
                            <ol>
                                <li>Clone the repository:
                                    <pre><code class="language-bash">git clone https://github.com/tashifkhan/sophos-auto-login.git
cd sophos-auto-login</code></pre>
                                </li>
                                <li>Install the required dependencies:
                                    <pre><code class="language-bash">pip install -r requirements.txt</code></pre>
                                </li>
                                <li>Run the script:
                                    <pre><code class="language-bash">python autologin.py</code></pre>
                                </li>
                            </ol>
                        </section>
                        
                        <section id="command-line" class="section">
                            <h2>Command-Line Usage</h2>
                            
                            <p>The script supports the following command-line arguments:</p>
                            
                            <div class="command">
                                <code>--start</code> or <code>-s</code>
                                <div class="command-desc">Start the auto-login process immediately <a href="#screenshots">[Screenshot]</a></div>
                            </div>
                            
                            <div class="command">
                                <code>--add</code> or <code>-a</code>
                                <div class="command-desc">Add new credentials to the database <a href="#screenshots">[Screenshot]</a></div>
                            </div>
                            
                            <div class="command">
                                <code>--edit</code> or <code>-e</code>
                                <div class="command-desc">Edit existing credentials</div>
                            </div>
                            
                            <div class="command">
                                <code>--delete</code> or <code>-del</code>
                                <div class="command-desc">Delete credentials from the database</div>
                            </div>
                            
                            <div class="command">
                                <code>--export [path]</code> or <code>-x [path]</code>
                                <div class="command-desc">Export credentials to a CSV file (optional path)</div>
                            </div>
                            
                            <div class="command">
                                <code>--import [path]</code> or <code>-i [path]</code>
                                <div class="command-desc">Import credentials from a CSV file</div>
                            </div>
                            
                            <div class="command">
                                <code>--show</code> or <code>-l</code>
                                <div class="command-desc">Display all stored credentials</div>
                            </div>
                            
                            <div class="command">
                                <code>--daemon</code> or <code>-d</code>
                                <div class="command-desc">Run the auto-login process in background mode (must be used with <code>--start</code>)</div>
                            </div>
                            
                            <div class="command">
                                <code>--exit</code> or <code>-q</code>
                                <div class="command-desc">Stop the daemon process and logout all credentials</div>
                            </div>
                            
                            <div class="command">
                                <code>--logout</code> or <code>-lo</code>
                                <div class="command-desc">Logout from all credentials without stopping the daemon process</div>
                            </div>
                            
                            <div class="command">
                                <code>--speedtest</code> or <code>-t</code>
                                <div class="command-desc">Run a speed test to measure your current internet connection performance</div>
                            </div>
                            
                            <div class="command">
                                <code>--status</code> or <code>-st</code>
                                <div class="command-desc">Display the current status of the daemon process <a href="#screenshots">[Screenshot]</a></div>
                            </div>

                            <div class="note">
                                <h3>Examples</h3>
                                <pre><code class="language-bash"># Start the auto-login process
python autologin.py --start

# Run in daemon mode (background process)
python autologin.py --start --daemon

# Stop the daemon process
python autologin.py --exit

# Add new credentials
python autologin.py --add

# Import credentials from CSV
python autologin.py --import credentials.csv</code></pre>
                            </div>
                        </section>

                        <section id="interactive-menu" class="section">
                            <h2>Interactive Menu</h2>
                            <p>If you run the script without any command-line arguments, it will present an interactive menu:</p>
                            <pre><code class="language-bash">python autologin.py</code></pre>
                            <p>This menu allows you to easily manage credentials and start the auto-login process without remembering specific commands. <a href="#screenshots">See an example screenshot</a> of the interactive menu.</p>
                            <p>Options include:</p>
                            <ul>
                                <li>Starting the auto-login process</li>
                                <li>Adding, editing, or deleting credentials</li>
                                <li>Showing all stored credentials</li>
                                <li>Importing/Exporting credentials via CSV</li>
                                <li>Running a speed test</li>
                                <li>Exiting the application</li>
                            </ul>
                        </section>

                        <section id="daemon-mode" class="section">
                            <h2>Daemon Mode</h2>
                            
                            <p>The daemon mode allows you to run the auto-login process in the background without keeping a terminal window open. This feature is only available on Unix-like systems (Linux, macOS).</p>
                            
                            <div class="note">
                                <p>When running in daemon mode:</p>
                                <ul>
                                    <li>The process detaches from the terminal and runs in the background</li>
                                    <li>All output is redirected to a log file in <code>~/.sophos-autologin/sophos-autologin.log</code></li>
                                    <li>A PID file is created at <code>~/.sophos-autologin/sophos-autologin.pid</code></li>
                                </ul>
                            </div>

                            <h3>Starting the Daemon</h3>
                            <pre><code class="language-bash">python autologin.py --start --daemon</code></pre>

                            <h3>Checking Daemon Status</h3>
                            <p>You can check if the daemon is running using the <code>--status</code> argument:</p>
                            <pre><code class="language-bash">python autologin.py --status</code></pre>
                            <p><a href="#screenshots">See an example screenshot</a> of the status output.</p>

                            <h3>Stopping the Daemon</h3>
                            <pre><code class="language-bash">python autologin.py --exit</code></pre>

                            <p>Alternatively, you can use the following command to find and kill the process:</p>
                            <pre><code class="language-bash">kill $(cat ~/.sophos-autologin/sophos-autologin.pid)</code></pre>
                        </section>

                        <section id="screenshots" class="section">
                            <h2>Screenshots</h2>
                            
                            <p>Here are some examples of the script in action:</p>

                            <h3>Interactive Menu</h3>
                            <div class="screenshot-container" style="text-align: center; margin: 1.5rem 0;">
                                <img src="{{ url_for('static', filename='screenshots/interative_menu.png') }}" alt="Interactive Menu" style="max-width: 100%; border-radius: 8px; border: 1px solid var(--border-color);">
                                <p><em>The main interactive menu providing various options.</em></p>
                            </div>

                            <h3>Starting Auto-Login</h3>
                            <div class="screenshot-container" style="text-align: center; margin: 1.5rem 0;">
                                <img src="{{ url_for('static', filename='screenshots/autologin-start.png') }}" alt="Start Auto-Login via CLI" style="max-width: 100%; border-radius: 8px; border: 1px solid var(--border-color);">
                                <p><em>Output when starting the auto-login process using <code>--start</code>.</em></p>
                            </div>
                            
                            <h3>Daemon Status</h3>
                            <div class="screenshot-container" style="text-align: center; margin: 1.5rem 0;">
                                <img src="{{ url_for('static', filename='screenshots/status.png') }}" alt="Daemon Status via CLI" style="max-width: 100%; border-radius: 8px; border: 1px solid var(--border-color);">
                                <p><em>Checking the status of the background daemon process using <code>--status</code>.</em></p>
                            </div>

                            <h3>Exit Daemon</h3>
                            <div class="screenshot-container" style="text-align: center; margin: 1.5rem 0;">
                                <img src="{{ url_for('static', filename='screenshots/exit.png') }}" alt="Exit Daemon via CLI" style="max-width: 100%; border-radius: 8px; border: 1px solid var(--border-color);">
                                <p><em>Stopping the daemon process and logging out using <code>--exit</code>.</em></p>
                            </div>

                            <h3>Logout</h3>
                            <div class="screenshot-container" style="text-align: center; margin: 1.5rem 0;">
                                <img src="{{ url_for('static', filename='screenshots/logout.png') }}" alt="Logout via CLI" style="max-width: 100%; border-radius: 8px; border: 1px solid var(--border-color);">
                                <p><em>Logging out from all active sessions using <code>--logout</code>.</em></p>
                            </div>

                            <h3>Speed Test</h3>
                            <div class="screenshot-container" style="text-align: center; margin: 1.5rem 0;">
                                <img src="{{ url_for('static', filename='screenshots/sppedtest.png') }}" alt="Speed Test via CLI" style="max-width: 100%; border-radius: 8px; border: 1px solid var(--border-color);">
                                <p><em>Running an internet speed test using <code>--speedtest</code>.</em></p>
                            </div>
                        </section>

                        <section id="additional-features" class="section">
                            <h2>Additional Features</h2>
                            
                            <h3>Automatic ID Switching</h3>
                            <p>The script automatically switches to the next available ID in the database if:</p>
                            <ul>
                                <li>The current ID reaches its data limit</li>
                                <li>The current ID fails to log in</li>
                            </ul>
                            <p>This ensures uninterrupted connectivity.</p>

                            <h3>Internet Connection Check</h3>
                            <p>The script periodically checks for internet connectivity every 90 seconds. If the internet connection is lost, the script will attempt to log in again.</p>

                            <h3>Scheduled Re-login</h3>
                            <p>To ensure continuous connectivity, the script performs a scheduled re-login every 30 minutes, even if the internet connection is active.</p>

                            <h3>Importing Previous CSV Files</h3>
                            <p>If you have previously used the CSV-based version of this script, you can directly import your existing CSV files:</p>
                            <pre><code class="language-bash">python autologin.py --import credentials.csv</code></pre>
                        </section>

                        <section id="creating-executable" class="section">
                            <h2>Creating an Executable</h2>
                            
                            <p>To create an executable from the Python script, follow these steps:</p>
                            
                            <ol>
                                <li>Clone the repository and navigate to the project directory:
                                    <pre><code class="language-bash">git clone https://github.com/tashifkhan/sophos-auto-login.git
cd sophos-auto-login</code></pre>
                                </li>
                                <li>Install the required dependencies:
                                    <pre><code class="language-bash">pip install -r requirements.txt</code></pre>
                                </li>
                                <li>Install PyInstaller:
                                    <pre><code class="language-bash">pip install pyinstaller</code></pre>
                                </li>
                                <li>Create the executable:
                                    <pre><code class="language-bash"># For MacOS / Linux
pyinstaller --onefile --add-data "db/credentials.db:." autologin.py

# For Windows
pyinstaller --onefile --add-data "db/credentials.db;." autologin.py</code></pre>
                                </li>
                            </ol>
                            
                            <p>This will create an executable file in the <code>dist</code> directory that you can run directly.</p>
                        </section>

                        <section id="macos-linux-setup" class="section">
                            <h2>macOS and Linux Setup</h2>
                            
                            <p>On Unix-based systems like macOS and Linux, you can set up the script to run as a standalone application with a virtual environment. This approach is more lightweight than creating an executable and provides better integration with the system.</p>
                            
                            <h3>Step 1: Creating a Virtual Environment</h3>
                            <p>A virtual environment isolates the script's dependencies from the system Python:</p>
                            
                            <pre><code class="language-bash"># Navigate to the project directory
cd sophos-auto-login

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt</code></pre>
                            
                            <h3>Step 2: Creating an Executable Script</h3>
                            <p>Make the Python script executable with a shebang line:</p>
                            
                            <ol>
                                <li>Add a shebang line to point to your virtual environment's Python interpreter:
                                    <pre><code class="language-python">#!/path/to/sophos-auto-login/venv/bin/python3

# Rest of your autologin.py content...</code></pre>
                                    <div class="note">
                                        <p>You can find the correct path by running:</p>
                                        <pre><code class="language-bash">which python</code></pre>
                                        <p>while your virtual environment is activated.</p>
                                    </div>
                                </li>
                                <li>Make the script executable:
                                    <pre><code class="language-bash">chmod +x autologin.py</code></pre>
                                </li>
                                <li>Now you can run the script directly:
                                    <pre><code class="language-bash">./autologin.py</code></pre>
                                </li>
                            </ol>
                            
                            <h3>Step 3: Creating a Launcher (Optional)</h3>
                            <p>You can create a shell script to easily run your application:</p>
                            
                            <pre><code class="language-bash">#!/bin/bash
# Save this as run_sophos.sh

# Navigate to the script directory
cd /path/to/sophos-auto-login

# Activate virtual environment and run the script
source venv/bin/activate
./autologin.py "$@"</code></pre>
                            
                            <p>Make the launcher executable:</p>
                            <pre><code class="language-bash">chmod +x run_sophos.sh</code></pre>
                            
                            <h3>Step 4: Creating a System Service (Linux)</h3>
                            <p>On Linux, you can create a systemd service to run the script at startup:</p>
                            
                            <pre><code class="language-ini">[Unit]
Description=Sophos Auto Login Service
After=network.target

[Service]
ExecStart=/path/to/sophos-auto-login/venv/bin/python3 /path/to/sophos-auto-login/autologin.py --start --daemon
WorkingDirectory=/path/to/sophos-auto-login
Restart=always
RestartSec=10
User=your_username

[Install]
WantedBy=multi-user.target</code></pre>
                            
                            <p>Save this file as <code>sophos-autologin.service</code> in <code>/etc/systemd/system/</code> and run:</p>
                            <pre><code class="language-bash">sudo systemctl enable sophos-autologin.service
sudo systemctl start sophos-autologin.service</code></pre>
                            
                            <h3>Step 5: Creating a Launch Agent (macOS)</h3>
                            <p>On macOS, you can create a Launch Agent to automatically start the script at login:</p>
                            
                            <pre><code class="language-xml">&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;Label&lt;/key&gt;
    &lt;string&gt;com.user.sophosautologin&lt;/string&gt;
    &lt;key&gt;ProgramArguments&lt;/key&gt;
    &lt;array&gt;
        &lt;string&gt;/path/to/sophos-auto-login/venv/bin/python3&lt;/string&gt;
        &lt;string&gt;/path/to/sophos-auto-login/autologin.py&lt;/string&gt;
        &lt;string&gt;--start&lt;/string&gt;
        &lt;string&gt;--daemon&lt;/string&gt;
    &lt;/array&gt;
    &lt;key&gt;RunAtLoad&lt;/key&gt;
    &lt;true/&gt;
    &lt;key&gt;KeepAlive&lt;/key&gt;
    &lt;true/&gt;
    &lt;key&gt;StandardErrorPath&lt;/key&gt;
    &lt;string&gt;/Users/your_username/.sophos-autologin/error.log&lt;/string&gt;
    &lt;key&gt;StandardOutPath&lt;/key&gt;
    &lt;string&gt;/Users/your_username/.sophos-autologin/output.log&lt;/string&gt;
    &lt;key&gt;WorkingDirectory&lt;/key&gt;
    &lt;string&gt;/path/to/sophos-auto-login&lt;/string&gt;
&lt;/dict&gt;
&lt;/plist&gt;</code></pre>
                            
                            <p>Save this file as <code>com.user.sophosautologin.plist</code> in <code>~/Library/LaunchAgents/</code> and run:</p>
                            <pre><code class="language-bash">launchctl load ~/Library/LaunchAgents/com.user.sophosautologin.plist</code></pre>
                            
                            <h3>Step 6: Using Aliases for Quick Access</h3>
                            <p>Add an alias to your shell configuration file (<code>~/.bashrc</code>, <code>~/.zshrc</code>, etc.):</p>
                            
                            <pre><code class="language-bash"># Add this to your shell configuration file
alias sophos-login="cd /path/to/sophos-auto-login && source venv/bin/activate && ./autologin.py"
alias sophos-start="sophos-login --start"
alias sophos-stop="sophos-login --exit"</code></pre>
                            
                            <p>After saving, reload your configuration:</p>
                            <pre><code class="language-bash">source ~/.bashrc  # or ~/.zshrc depending on your shell</code></pre>
                            
                            <p>Now you can use simple commands from anywhere:</p>
                            <pre><code class="language-bash">sophos-start    # Start the auto-login process
sophos-stop     # Stop the process and logout</code></pre>
                        </section>

                        <footer>
                            <p>Sophos Auto Login is <a href="https://github.com/tashifkhan/sophos-auto-login">open source and available on GitHub</a></p>
                            <span class="footer-dev">Developed by <a href="https://portfolio.tashif.codes" target="_blank">Tashif Ahmad Khan</a></span>
                        </footer>
                    </div>
                </div>
            </div>

            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markup.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-ini.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>

            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    const menuToggle = document.getElementById('menuToggle');
                    const sidebar = document.getElementById('sidebar');
                    const overlay = document.getElementById('overlay');
                    
                    menuToggle.addEventListener('click', function() {
                        sidebar.classList.toggle('open');
                        overlay.classList.toggle('active');
                    });
                    
                    overlay.addEventListener('click', function() {
                        sidebar.classList.remove('open');
                        overlay.classList.remove('active');
                    });

                    function scrollToElement(elementId) {
                        const targetElement = document.getElementById(elementId);
                        if (targetElement) {
                            window.scrollTo({
                                top: targetElement.offsetTop - 70,
                                behavior: 'smooth'
                            });
                            document.querySelectorAll('.nav-item').forEach(item => {
                                item.classList.remove('active');
                                const link = item.querySelector(`a[href="#${elementId}"]`);
                                if (link) {
                                    item.classList.add('active');
                                }
                            });
                        }
                    }

                    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                        anchor.addEventListener('click', function (e) {
                            e.preventDefault();
                            
                            sidebar.classList.remove('open');
                            overlay.classList.remove('active');
                            
                            const targetId = this.getAttribute('href').substring(1);
                            
                            history.pushState(null, null, `#${targetId}`); 
                            
                            scrollToElement(targetId);
                        });
                    });

                    if (window.location.hash) {
                        const initialTargetId = window.location.hash.substring(1);
                        setTimeout(() => {
                            scrollToElement(initialTargetId);
                        }, 100); 
                    } else {
                         const firstNavItem = document.querySelector('.nav-item');
                         if (firstNavItem) {
                             firstNavItem.classList.add('active');
                         }
                    }
                    
                    window.addEventListener('scroll', function() {
                        const sections = document.querySelectorAll('section[id]');
                        let currentSection = '';
                        const scrollPosition = window.scrollY;
                        
                        sections.forEach(section => {
                            const sectionTop = section.offsetTop - 80;
                            const sectionHeight = section.offsetHeight;
                            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                                currentSection = section.getAttribute('id');
                            }
                        });

                        if (scrollPosition < sections[0].offsetTop - 80) {
                             currentSection = sections[0].getAttribute('id');
                        }
                        const lastSection = sections[sections.length - 1];
                        if (scrollPosition + window.innerHeight >= document.documentElement.scrollHeight - 50) {
                             currentSection = lastSection.getAttribute('id');
                        }
                        
                        if (currentSection) {
                            document.querySelectorAll('.nav-item').forEach(item => {
                                item.classList.remove('active');
                                const link = item.querySelector('a');
                                if (link && link.getAttribute('href') === '#' + currentSection) {
                                    item.classList.add('active');
                                }
                            });
                        } else if (!window.location.hash) {
                             const firstNavItem = document.querySelector('.nav-item');
                             if (firstNavItem) {
                                 document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
                                 firstNavItem.classList.add('active');
                             }
                        }
                    });

                    document.querySelectorAll('pre').forEach(block => {
                        if (!block.querySelector('.copy-button')) {
                            const button = document.createElement('button');
                            button.className = 'copy-button';
                            button.textContent = 'Copy';
                            
                            const message = document.createElement('span');
                            message.className = 'copied-message';
                            message.textContent = 'Copied!';
                            
                            button.addEventListener('click', () => {
                                const code = block.querySelector('code');
                                const range = document.createRange();
                                range.selectNode(code);
                                window.getSelection().removeAllRanges();
                                window.getSelection().addRange(range);
                                
                                try {
                                    const successful = document.execCommand('copy');
                                    if (successful) {
                                        message.classList.add('show');
                                        setTimeout(() => {
                                            message.classList.remove('show');
                                        }, 1500);
                                    }
                                } catch (err) {
                                    console.error('Failed to copy: ', err);
                                }
                                
                                window.getSelection().removeAllRanges();
                            });
                            
                            block.appendChild(button);
                            block.appendChild(message);
                        }
                    });
                    
                    document.querySelectorAll('pre code:not([class*="language-"])').forEach(block => {
                        let text = block.textContent.trim().toLowerCase();
                        let language = '';
                        
                        if (text.includes('python') || text.includes('import') || text.includes('def ') || 
                            text.startsWith('#!/usr/bin/env python') || text.includes('.py')) {
                            language = 'language-python';
                        } else if (text.includes('apt-get') || text.includes('sudo') || text.includes('chmod') || 
                                   text.includes('cd ') || text.includes('mkdir') || text.startsWith('#!/bin/bash') || 
                                   text.includes('.sh')) {
                            language = 'language-bash';
                        } else if (text.includes('<dict>') || text.includes('<?xml') || text.includes('</plist>') || 
                                   text.includes('<key>') || text.includes('</key>')) {
                            language = 'language-markup';
                        } else if (text.includes('[unit]') || text.includes('[service]') || text.includes('[install]')) {
                            language = 'language-ini';
                        }
                        
                        if (language) {
                            block.className = language;
                            Prism.highlightElement(block);
                        }
                    });
                });
            </script>
        </body>
        </html>
    """
    return render_template_string(html)


if __name__ == '__main__':
    app.run(debug=True, port=7546, threaded=True)
