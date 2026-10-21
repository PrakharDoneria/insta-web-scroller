# Insta Web Scroller

A small Selenium project that opens Instagram Reels in Microsoft Edge, lets
each Reel play, and automatically moves to the next Reel.

## Features

- Uses a separate Edge testing profile so your normal Edge session can remain
  open.
- Opens `https://www.instagram.com/reels/`.
- Waits for you to log in to Instagram in the testing profile.
- Prints a success message after detecting the Reels page.
- Detects the current HTML5 video's duration and waits for playback to finish
  or loop.
- Scrolls to the next Reel using mouse-wheel input with a keyboard fallback.
- Stops cleanly with `Ctrl+C`.

## Requirements

- Windows
- Python 3.10 or newer
- Microsoft Edge
- An Instagram account

Selenium Manager normally downloads and selects the matching Edge WebDriver
automatically. Internet access may be required the first time Selenium starts.

## Installation

Open PowerShell in this project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, install the dependency without activating the
environment:

```powershell
python -m pip install -r requirements.txt
```

## Run

```powershell
python -u .\main.py
```

On the first run:

1. A separate Edge window opens.
2. Log in to Instagram in that window.
3. The script opens the Reels page and reports success.
4. Watch the current Reel; the script advances when playback finishes or
   loops.

The separate profile is saved at:

```text
C:\Users\<your-user>\insta-web-scroller-edge-profile
```

This profile keeps its own Instagram login. Your regular Edge profile is not
modified.

## Stop the scroller

Press `Ctrl+C` in the PowerShell window running the script. The Edge testing
window will close and the script will exit.

## Troubleshooting

### The browser does not open

Make sure Microsoft Edge is installed and close any old scroller Edge window.
Then run the command again.

### Instagram asks me to log in every time

Log in to Instagram in the Edge window opened by the script, not in your
regular Edge window. Do not delete the profile directory unless you want to
start with a fresh login.

### The script does not advance

Make sure the Reels page is visible and the video is not blocked by a browser
permission prompt. The script advances when the video ends, loops, or stops
reporting playback progress.

### Instagram changes its page behavior

Instagram is a dynamic website, so DOM and playback behavior can change.
Automation may need adjustments if Instagram changes its Reels interface.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Edge automation and Reels scrolling logic |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Excludes local profiles, caches, and environment files |

## Responsible use

Use the project only for your own account and normal personal viewing. Do not
use it to bypass Instagram security, automate likes/comments/follows, or
collect content or personal data.
