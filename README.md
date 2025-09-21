#  ZenSocial

ZenSocial is the community platform for **ZenCommunity**. It ships a modern three-column social UI (dark theme with the signature Zen-green) and a simple Write-to-Earn model so creators can see value from engagement.

**Access**: You can only **log in with a minted ZenID**. No other login methods are enabled.

---

## 📌 Overview

**What it is**: A fast, minimal Social / SocialFi MVP where users post, interact, message (demo), view notifications, manage profile, and see Earn totals.

**How you log in**: Mint a ZenID → use that ZenID to sign in.

**What’s special**: A transparent Write-to-Earn formula that converts engagement into $ZTC.

**Write-to-Earn** (current formula, in $ZTC)

**earnings** = likes * 0.01 + comments * 0.02 + reposts * 0.05

---

## Features & Screens

+ **Home** – Composer + Create-Post modal (text, image/video preview), like/repost/comment with live counters, collapsible comment list, right sidebar with Search + “What’s happening”.

+ **Messages** – Demo conversation with ZenCommunity (avatar loads from static/images/zenchain2_bg.* with extension fallback). Simple composer (button or Enter). (Template included; add a route if you want it live.)

+ **Notifications** – Tabs All / Verified / Mentions (client-side filter) with varied demo items (follow, like, ZenShield alert, community pin). Right sidebar mirrors Home.

+ **Profile** – Edit avatar, cover, name, bio; personal posts render with full interactions; comment list toggle.

Earn – Shows totals (likes / comments / reposts) and computed $ZTC from the formula above. Empty state includes a gentle CTA.
---

## Tech Stack

1. **Backend**: Flask (Python), SQLite (auto-init on first run)

2. **Frontend**: HTML/CSS/JS, Font Awesome, Inter font

3. **Assets & Uploads**: under static/ (uploads saved to static/uploads/)

---

## Setup & Run (local)

# Python 3.10+ recommended
pip install flask

# run
python app.py
# open
http://127.0.0.1:5000

+ On first run, the SQLite database is created automatically (user.db).

+ Uploads (avatar/cover/media) are saved under static/uploads/.

## 📂 Project Structure
/static
  /images
    zenchain2_bg.(png|jpg|jpeg|webp)   # avatar for ZenCommunity demo
  default_avatar.png
  default_cover.jpg
  /uploads                             # created automatically for media
/templates
  index.html           # Home
  profile.html         # Profile
  earn.html            # Earn
  messenger.html       # Messages (demo UI)
  notifications.html   # Notifications (demo UI)
  login.html           # ZenID login / mint
app.py                 # Flask app & routes

## 📝 Conclusion
**ZenSocial** is a focused, working social surface for **ZenCommunity**—no extras, no speculation. Access is **ZenID-only** (you mint a ZenID and use it to sign in), and value is computed with a clear **Write-to-Earn** rule:

**earnings** = likes * 0.01 + comments * 0.02 + reposts * 0.05  (in $ZTC)

**What you get today**: a clean three-column UI; posting with media preview; live interactions (likes/reposts/comments); a Messages demo thread; Notifications with simple tabs; Profile editing; and an Earn view that shows exactly how engagement adds up. Built with Flask + SQLite + HTML/CSS/JS, it’s fast to run, easy to read, and ready for your community.

**Mint a ZenID → sign in → post → engage → see $ZTC in Earn**.

