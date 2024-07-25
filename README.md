# THIS PROJECT IS STILL UNDER HEAVY DEVELOPMENT - TRUST ME

# M-Track

M-Track is a web application designed to track and display detailed statistics for League of Legends players. It provides valuable insights into match history, player performance, and more.

## Table of Contents

- [THIS PROJECT IS STILL UNDER HEAVY DEVELOPMENT](#this-project-is-still-under-heavy-development)
- [M-Track](#m-track)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Personal Notes](#personal-notes)

## Features

- **Match History:** View detailed information about your recent League of Legends matches.
- **Player Stats:** Analyze your performance with statistics on kills, deaths, assists, and more.
- **Summoner Search:** Look up other players' profiles by summoner name.
- **Data Updates:** Keep your match history up-to-date with on demand data fetching.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python
- Flask
- MySQL (or another supported database)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/noahpop77/M-Track.git
   ```

2. Move into the directory:

   ```bash
   cd M-Track
   ```

3. Install the requirements:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the flask server:

   ```bash
   cd flask
   python3 routes.py
   ```

## Personal Notes

To start the app go into the correct directory and run the routes.py file.

```bash
sawa@sawa:~/mainShare/devenv/gitrepos/M-Track/flask$ sudo python3 routes.py
```

For now I will be working out of the `http://10.0.0.150/matchHistory` site.

This spawns from the projects web server to refine the process of performign all of the API and SQL calls in the back end and making the front end more digestable. Also revise the data schema in the backend.

- Working out of my ubuntu server for now.
- This is a great tool for working with the data to format it
  - `https://jsonformatter.curiousconcept.com/#`
- Riot games developer portal
  - `https://developer.riotgames.com/`
- Riot developer website page on riotIDs and summoner names
  - `https://developer.riotgames.com/docs/lol#summoner-names-to-riot-ids`
    - `https://developer.riotgames.com/apis#account-v1/GET_getByRiotId`
    - `https://developer.riotgames.com/docs/lol#data-dragon_items`
- All League of Legends visual assets (splashes, tiles, runes, everything)
  - `https://riot-api-libraries.readthedocs.io/en/latest/ddragon.html`
- Riot IDs that I can use for testing:
  - `https://www.op.gg/summoners/na/Chaddam-NA1`
    - `Chaddam#NA1`
    - `Uday#6666`
  - `https://www.op.gg/summoners/na/Scyrnn-NA1`
    - `Scyrnn#NA1`
- Sprite Sheet maker

  - `https://www.codeandweb.com/free-sprite-sheet-packer`

- For some reason this user has a riot ID name and tagline but doesnt have a summoner name. So watch out.
  - https://www.op.gg/summoners/na/BARRRRRRRREL-GPGOD

# Future Ideas

- Scalable Cloud Infrastructure
  - AWS RDS for database
  - Host web server
  - Containerize webapp for scalability
- FAST API
  - Faster performing API (look into testing it)
- On hover item description
- Clicking on a team mates name will take you to their profile
- Function to filter match history for specific champion
  - Dropdown
  - List
  - Search Bar
  - whatever
- Profile Stat Card
  - (Like the stats on the left )




# TODO

New fix for CORS problem experienced when using https://mtrack.lol vs https://www.mtrack.lol.
The actual requests need to be changed. The line that contains the value for Access-Control-Allow-Origin needs to be *.

Not working line:
```javascript
await fetch(url, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://www.mtrack.lol/",
        "Access-Control-Allow-Credentials": "true"
    },
    body: JSON.stringify(requestBody)
})
```

Hypothesized working line:
```javascript
await fetch(url, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true"
    },
    body: JSON.stringify(requestBody)
})
```




Built in utility that auto updates image assets for the website.


ADD LP NUMBER NOT JUST RANK NAME

