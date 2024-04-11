async function summonerSearch(summonerNameParam) {
    var url = "https://www.mtrack.lol/summonerSearch";

    var responseParagraph = document.getElementById('responseParagraph');
    // Use the provided summonerNameParam if available; otherwise, use the input value
    var summonerName = summonerNameParam || document.getElementById("nameInput").value;

    // Get the select element
    var selectElement = document.getElementById('region');
    var regionSelect = selectElement.value;
    console.log(regionSelect);

    var requestBody = {
        summonerName: summonerName,
        regionSelect: regionSelect
    };
    

    responseParagraph.textContent = "Searching for Summoner...";

    await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://www.mtrack.lol/",
            "Access-Control-Allow-Credentials": "true"
        },
        body: JSON.stringify(requestBody)
    })
    .then(function(response) {
        // Check if the response was successful
        if (response.ok) {
            return response.json(); // Convert response to text
        } else {
            throw new Error('Error: ' + response.status); // Throw an error
        }
    })
    .then(function(data) {
        const dataContainer = document.getElementById('data-container');
        dataContainer.innerHTML = '';
        /////////////////////////////////////////////////
        const riotID = document.getElementById('nameInput').value;
        rankSearch(riotID);
        printMatches(data.gameData, data.playerStats, data.matchData, data.riotID);
    })
    .catch(function(error) {
        responseParagraph.textContent = "Summoner not found..."
        console.log(error)
        // Display error message
    });
}


async function showMore() {
    var url = "https://www.mtrack.lol/showMore";
    var showMoreButtonTag = document.getElementById('showMoreButtonTag');
    showMoreButtonTag.innerText = "Loading more games...";


    const matchCardTags = document.querySelectorAll('[id="matchCard"]');
    const excludeGameIDs = Array.from(matchCardTags).map(tag => tag.getAttribute('data-gameID'));

    const searchedUser = document.getElementById('nameInput').value;

    // Get the select element
    var selectElement = document.getElementById('region');
    var regionSelect = selectElement.value;
    console.log(regionSelect);

    var requestBody = {
        searchedUser: searchedUser,
        excludeGameIDs: excludeGameIDs,
        regionSelect: regionSelect
    };
    
    await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://www.mtrack.lol/",
            "Access-Control-Allow-Credentials": "true"
        },
        body: JSON.stringify(requestBody)
    })
    .then(function(response) {
        // Check if the response was successful
        if (response.ok) {
            return response.json(); // Convert response to text
        } else {
            throw new Error('Error: ' + response.status); // Throw an error
        }
    })
    .then(function(data) {
        showMoreButtonTag.innerText = "SHOW MORE";

        printMatches(data.gameData, data.playerStats, data.matchData, data.riotID);
    })
    .catch(function(error) {
        // responseParagraph.textContent = "Summoner not found..."
        console.log(error)
        // Display error message
    });
}


async function updateData() {
    var url = "https://www.mtrack.lol/getHistory";

    var responseParagraph = document.getElementById('responseParagraph');
    responseParagraph.textContent = "Getting history...";
    var riotID = document.getElementById("nameInput").value;

    // Get the select element
    var selectElement = document.getElementById('region');
    var regionSelect = selectElement.value;
    console.log(regionSelect);

    var requestBody = {
        regionSelect: regionSelect,
        riotID: riotID
    };

    await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://www.mtrack.lol/",
            "Access-Control-Allow-Credentials": "true"
        },
        body: JSON.stringify(requestBody)
    })
    .then(function(response) {
        // Check if the response was successful
        if (response.ok) {
            return response.json(); // Convert response to text
        } else {
            throw new Error('Error: ' + response.status); // Throw an error
        }
    })
    .then(function(data) {
        /////////////////////////////////////////////////
        const dataContainer = document.getElementById('data-container');
        dataContainer.innerHTML = '';
        const riotID = document.getElementById('nameInput').value;
        rankSearchUpdate(riotID);
        //responseParagraph.textContent = "Updated, Please Refresh";
        
        printMatches(data.gameData, data.playerStats, data.matchData, data.riotID);
    })
    .catch(function(error) {
        responseParagraph.textContent = error.message; // Display error message
    });
}


// TODO: REWORK: Make it so that the assets in the accordion item are only loaded if the user clicks on the game card to view the information within it.
async function toggleAccordion(header) {
    // Get the parent accordion item
    var accordionItem = header.parentNode;
    // Toggle the "active" class to show/hide the accordion body
    accordionItem.classList.toggle("active");
}



function calculateKDA(kills, deaths, assists) {

    if (deaths === 0) {
        return 'Infinity';
    }

    const kda = (kills + assists) / deaths;

    return kda.toFixed(2);
}

function riotIDSplitter(inputString) {
    // Splitting the string at the '#' symbol
    const nameParts = inputString.split("#");
  
    // Extracting the parts
    const gamename = nameParts[0];
    const tag = nameParts[1] || null;
  
    // Returning the results
    return {
      gamename,
      tag
    };
}

function generateRandomNumber() {
    const length = 10;
    let randomNumber = '';

    for (let i = 0; i < length; i++) {
        randomNumber += Math.floor(Math.random() * 10);
    }

    return randomNumber;
}

function winrateCalculator(wins, losses) {
    wins = parseInt(wins, 10);
    losses = parseInt(losses, 10);

    var totalGamesPlayed = wins + losses;
    var winrateFloat = wins / totalGamesPlayed * 100;
    var winrate = Math.round(winrateFloat, 1)
    return winrate;
}

function itemToClass(itemName) {
    const itemClassName = itemName.replace(/ /g, '-').replace(/'/g, '_');
    return itemClassName;
}


async function rankSearch(riotIDParam) {
    var url = "https://www.mtrack.lol/getRank";

    // Use the provided summonerNameParam if available; otherwise, use the input value
    var riotID = riotIDParam || document.getElementById("nameInput").value;

    // Get the select element
    var selectElement = document.getElementById('region');
    var regionSelect = selectElement.value;

    var requestBody = {
        riotID: riotID,
        regionSelect: regionSelect
    };

    await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://www.mtrack.lol/",
            "Access-Control-Allow-Credentials": "true"
        },
        body: JSON.stringify(requestBody)
    })
    .then(function(response) {
        // Check if the response was successful
        if (response.ok) {
            return response.json(); // Convert response to text
        } else {
            throw new Error('Error: ' + response.status); // Throw an error
        }
    })
    .then(function(data) {
        const dataContainer = document.getElementById('player-container');
        dataContainer.innerHTML = `
        <div class="center searchSection text-dark text-center fw-bold" style="border-top-left-radius: 15px; border-top-right-radius: 15px; font-family: VCR OSD Mono, sans-serif; font-size: 100%; width: 740px; display: flex; justify-content: center;">
            <div class="nested-container" style="justify-content: center;">
                ${data[0].queueType}
            </div>
        </div>
        <div class="center searchSection text-dark text-center fw-bold" style="font-family: VCR OSD Mono, sans-serif; font-size: 100%; width: 740px; display: flex; justify-content: center;">
            <div class="nested-container" style="justify-content: center;">
                 ${data[0].tier} ${data[0].rank}
            </div>
        </div>
        <div class="center searchSection text-dark text-center fw-bold" style="font-family: VCR OSD Mono, sans-serif; font-size: 100%; width: 740px; display: flex; justify-content: center;">
            <div class="nested-container" style="justify-content: center;">
                Wins: ${data[0].wins} / Losses: ${data[0].losses}
            </div>
        </div>
        <div class="center searchSection text-dark text-center fw-bold" style="border-bottom-left-radius: 15px; border-bottom-right-radius: 15px; font-family: VCR OSD Mono, sans-serif; font-size: 100%; width: 740px; display: flex; justify-content: center;">
            <div class="nested-container" style="justify-content: center;">
                Win Rate ${winrateCalculator(data[0].wins, data[0].losses)}%
            </div>
        </div>
        `;
    })
    .catch(function(error) {
        console.log(error)
        const dataContainer = document.getElementById('player-container');
        dataContainer.innerHTML = `
        <div class="center searchSection text-dark text-center fw-bold" style="font-family: VCR OSD Mono, sans-serif; font-size: 100%; width: 740px; display: flex; justify-content: center;">
            <div class="nested-container" style="justify-content: center;">
                Not valid ranked data(Placements not done or wrong region)
            </div>
        </div>
        `;
    });
}



async function rankSearchUpdate(riotIDParam) {
    var url = "https://www.mtrack.lol/updateRank";

    // Use the provided summonerNameParam if available; otherwise, use the input value
    var riotID = riotIDParam || document.getElementById("nameInput").value;

    // Get the select element
    var selectElement = document.getElementById('region');
    var regionSelect = selectElement.value;
    console.log(regionSelect);

    var requestBody = {
        riotID: riotID,
        regionSelect: regionSelect
    };

    await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://www.mtrack.lol/",
            "Access-Control-Allow-Credentials": "true"
        },
        body: JSON.stringify(requestBody)
    })
    .then(function(response) {
        // Check if the response was successful
        if (response.ok) {
            return response.json(); // Convert response to text
        } else {
            throw new Error('Error: ' + response.status); // Throw an error
        }
    })
    .then(function(data) {
        const dataContainer = document.getElementById('player-container');
        dataContainer.innerHTML = `
        <div class="center searchSection text-dark text-center fw-bold" style="border-top-left-radius: 15px; border-top-right-radius: 15px; font-family: VCR OSD Mono, sans-serif; font-size: 100%; width: 740px; display: flex; justify-content: center;">
            <div class="nested-container" style="justify-content: center;">
                ${data[0].queueType}
            </div>
        </div>
        <div class="center searchSection text-dark text-center fw-bold" style="font-family: VCR OSD Mono, sans-serif; font-size: 100%; width: 740px; display: flex; justify-content: center;">
            <div class="nested-container" style="justify-content: center;">
                 ${data[0].tier} ${data[0].rank}
            </div>
        </div>
        <div class="center searchSection text-dark text-center fw-bold" style="font-family: VCR OSD Mono, sans-serif; font-size: 100%; width: 740px; display: flex; justify-content: center;">
            <div class="nested-container" style="justify-content: center;">
                Wins: ${data[0].wins} / Losses: ${data[0].losses}
            </div>
        </div>
        <div class="center searchSection text-dark text-center fw-bold" style="border-bottom-left-radius: 15px; border-bottom-right-radius: 15px; font-family: VCR OSD Mono, sans-serif; font-size: 100%; width: 740px; display: flex; justify-content: center;">
            <div class="nested-container" style="justify-content: center;">
                Win Rate ${winrateCalculator(data[0].wins, data[0].losses)}%
            </div>
        </div>
        `;
    })
    .catch(function(error) {
        console.log(error)
        const dataContainer = document.getElementById('player-container');
        dataContainer.innerHTML = `
        <div class="center searchSection text-dark text-center fw-bold" style="font-family: VCR OSD Mono, sans-serif; font-size: 100%; width: 740px; display: flex; justify-content: center;">
            <div class="nested-container" style="justify-content: center;">
                Not valid ranked data(Placements not done or wrong region)
            </div>
        </div>
        `;
    });
}



// TODO: REWORK: Make it so that the assets in the accordion item are only loaded if the user clicks on the game card to view the information within it.
async function printMatches(gameDataIn, playerStatsIn, matchData, summonerName) {
    // Assuming gameData and playerStats are available as arrays of objects
    const gameData = gameDataIn;
    const playerStats = playerStatsIn;
    
    var responseParagraph = document.getElementById('responseParagraph');
    responseParagraph.textContent = summonerName;
    responseParagraph.innerHTML = `
    <div class="container-fluid">
        <div class="row">
            <div class="col-2">
                <button id="updateButton" class="btn btn-dark btn-sm rounded-3" style="font-weight:bold; font-size: 50%; font-family: VCR OSD Mono, sans-serif; outline: none; box-shadow: none; padding: 7px;" onclick="updateData()">Update</button>
                </div>
                <div class="col-8 d-flex justify-content-center align-items-center">
                <h3 id="searchedUser" class="fw-bold" style="font-family: VCR OSD Mono, sans-serif; font-size: 100%;">${summonerName}</h3>
            </div>
            <div class="col-2"></div>
        </div>
    </div>
    `;



    let container;
    if (document.getElementById('matchHistoryFeed')) {
        container = document.getElementById('matchHistoryFeed');
    }
    else {
        // Create a new div element with a custom ID
        container = document.createElement('div');
        container.id = `matchHistoryFeed`;
    }

    
    // Get the data-container element
    const dataContainer = document.getElementById('data-container');
    // Clear existing content in the data-container
    dataContainer.innerHTML = '';


    // Gets a value from the formControl div on the main page. This value is then iterated for as many times as the same page calls the printMatches function meaning how many times they hit the SHOW MORE button.
    formControl = document.getElementById('formControl')
    const dataKey = formControl.getAttribute('data-key');
    cardCount = dataKey + 7
    formControl.setAttribute('data-key', cardCount);

    


    // Loop through the arrays simultaneously using forEach
    gameData.forEach((row1, index) => {
        
        const row2 = playerStats[index];
        const row3 = matchData[index];

        // Access the array and separate based on the 'win' field
        const winners = row3.filter(obj => obj.win === true);
        const losers = row3.filter(obj => obj.win === false);

        const primaryTableID = `primaryTable_${index}_${cardCount}`;
        const secondaryTableID = `secondaryTable_${index}_${cardCount}`;

        // Error handling for when a user has changed their name
        // If the match history detects that a user has changed their name the
        // if (row2.win == true && row2.riotID.toLowerCase() == summonerName.toLowerCase())
        // conditional wont work and will throw a row2 undefined TypeError.
        // This block of code catches that and catches the undefined TypeError of possibly
        // trying to remove the showmore button multiple times.
        if (typeof row2 == 'undefined'){
            try {
                var removeShowMore = document.getElementById("showMoreButtonTag");
                removeShowMore.remove();
            } catch (error) {}
            return;
        }


        if (row2.win == true && row2.riotID.toLowerCase() == summonerName.toLowerCase()) {
            
            // TODO: These items can be turned into sprites
            
            kda = calculateKDA(row2.kills, row2.deaths, row2.assists);
            
            player1Name = row3[0].riotID;
            player2Name = row3[1].riotID;
            player3Name = row3[2].riotID; 
            player4Name = row3[3].riotID; 
            player5Name = row3[4].riotID; 
            player6Name = row3[5].riotID; 
            player7Name = row3[6].riotID; 
            player8Name = row3[7].riotID; 
            player9Name = row3[8].riotID; 
            player10Name = row3[9].riotID;

            //Gets the Kill participation
            var killTotalTeam = 0;
            row3.forEach(player => {
                if (player.playerTeamID == row2.playerTeamID) {
                    killTotalTeam = killTotalTeam + player.kills;
                };
            });
            participation = Math.round((row2.kills / killTotalTeam) * 100);

            if (isNaN(participation)){
                participation = 0;
            }

            // Gets cs per minute
            csPerMinFloat = row2.totalCS / parseInt(row1.gameDurationMinutes.slice(0, -3));
            csPerMin = csPerMinFloat.toFixed(1);

            // Takes data and submits it to the header of the tag for usage if referenced
            // <div style="display: flex; background-color: #28344e; color: white;" class="accordion-header flex" data-win="win" data-card-count="${cardCount}" data-winners="${JSON.stringify(winners)}" data-losers="${JSON.stringify(losers)}" onclick='toggleAccordion(this)'>
            container.innerHTML += `
            <div style="background-color: #28344e; border-radius: 15px;" class="accordion-item" data-gameID="${row1.gameID}" id="matchCard">
                <div style="display: flex; background-color: #28344e; color: white;" class="accordion-header flex" onclick='toggleAccordion(this)'>
                
                    <div class="nested-container">
                    <div style="border-radius: 15px; width: 35px; background-color: rgb(83, 131, 232);"></div>
                        <div class="item-container rankedGameCard">
                            <div class="innerCard">
                                <p class="match-card-text" style="color: #336be3;"><b>Ranked Solo</b></p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text">${row1.gameDate}</p>
                            </div>
                            <div class="winDivider"></div>
                            <div class="innerCard">
                                <p class="match-card-text"><b>Victory</b></p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text">${row1.gameDurationMinutes}</p>
                            </div>
                        </div>

                        <div class="item-container portraitCard">
                            <div class="innerCard">
                                
                                <div class="image-container">
                                    <img class="${row2.Champ}">
                                    <div class="text-over-image">${row2.champLevel}</div>
                                </div>
                                <div style="flex-direction: row;">
                                    <img class="${row2.summonerSpell1}">
                                    <img class="${row2.summonerSpell2}">
                                </div>
                            </div>
                        </div>



                        <div style="padding-top: 5px;">
                            <div class="">
                                <img class="${itemToClass(row2.keystone)}">
                                <img class="${itemToClass(row2.secondaryRune)}">
                            </div>
                        </div>

                        <div style="padding-top: 5px;">
                            <div class="">
                                <img class="${itemToClass(row2.item0)}">
                                <img class="${itemToClass(row2.item1)}">
                                <img class="${itemToClass(row2.item2)}">
                            </div>
                        </div>
                        <div style="padding-top: 5px;">
                            <div class="">
                                <img class="${itemToClass(row2.item3)}">
                                <img class="${itemToClass(row2.item4)}">
                                <img class="${itemToClass(row2.item5)}">
                            </div>
                        </div>
                        <div style="padding-top: 5px;">
                            <div class="">
                                <img style="margin-top: 25px; border-radius: 50%;" class="${itemToClass(row2.item6)}">
                            </div>
                        </div>
                        

                        <div class="item-container px-2">
                            <div class="innerCard">
                                <p class="kda">${row2.kills} / <span style="color: #e84057">${row2.deaths}</span> / ${row2.assists}</p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text" style="color: #7c7e97; font-weight:400;">${kda}:1 KDA</p>
                            </div>
                            <div class="winDivider"></div>
                            <div class="innerCard">
                                <p class="match-card-text" style="color: #336be3"><b>K/P: ${participation}%</b></p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text">CS ${row2.totalCS} (${csPerMin})</p>
                            </div>
                            
                        </div>
                        
                        <div class="item-container teamCard">
                            <div class="innerCard">
                                <img class="${row3[0].Champ}Scoreboard">
                                <img class="${row3[1].Champ}Scoreboard">
                                <img class="${row3[2].Champ}Scoreboard">
                                <img class="${row3[3].Champ}Scoreboard">
                                <img class="${row3[4].Champ}Scoreboard">
                            </div>
                        </div>
                        <div class="item-container teamName">
                            <div class="innerCard">
                                <div>${player1Name}</div>
                                <div>${player2Name}</div>
                                <div>${player3Name}</div>
                                <div>${player4Name}</div>
                                <div>${player5Name}</div>
                            </div>
                        </div>

                        <div class="item-container teamCard ">
                            <div class="innerCard">
                                <img class="${row3[5].Champ}Scoreboard">
                                <img class="${row3[6].Champ}Scoreboard">
                                <img class="${row3[7].Champ}Scoreboard">
                                <img class="${row3[8].Champ}Scoreboard">
                                <img class="${row3[9].Champ}Scoreboard">
                            </div>
                        </div>
                        <div class="item-container teamName">
                            <div class="innerCard">
                                <div>${player6Name}</div>
                                <div>${player7Name}</div>
                                <div>${player8Name}</div>
                                <div>${player9Name}</div>
                                <div>${player10Name}</div>
                            </div>
                        </div>

                    </div>
                </div>
                
                
                
                <table class="accordion-body" style="color: white;">
                    <colgroup>
                        <col width="20%">
                        <col width="5%">
                        <col width="25%">
                        <col width="5%">
                        <col width="10%">
                        <col width="5%">
                        <col width="30%">
                    </colgroup>
                    <thead>
                        <tr style="text-align: center;">
                        <th colspan="3">Your Team</th>
                            <th>KDA</th>
                            <th>Damage</th>
                            <th>CS</th>
                            <th>Items</th>
                        </tr>
                    </thead>
                    

                    <tbody id="${primaryTableID}">
                    </tbody>
                </table>

                <table class="accordion-body" style="color: white;">
                    <colgroup>
                        <col width="20%">
                        <col width="5%">
                        <col width="25%">
                        <col width="5%">
                        <col width="10%">
                        <col width="5%">
                        <col width="30%">
                    </colgroup>
                    <thead>
                        <tr style="text-align: center;">
                            <th colspan="3">Enemy Team</th>
                            <th>KDA</th>
                            <th>Damage</th>
                            <th>CS</th>
                            <th>Items</th>
                        </tr>
                    </thead>
                    <tbody id="${secondaryTableID}">
                    </tbody>
                </table>
            </div>
            `;
          } 


          else {

            kda = calculateKDA(row2.kills, row2.deaths, row2.assists);



            player1Name = row3[0].riotID;
            player2Name = row3[1].riotID;
            player3Name = row3[2].riotID; 
            player4Name = row3[3].riotID; 
            player5Name = row3[4].riotID; 
            player6Name = row3[5].riotID; 
            player7Name = row3[6].riotID; 
            player8Name = row3[7].riotID; 
            player9Name = row3[8].riotID; 
            player10Name = row3[9].riotID;

            //Gets the Kill participation
            var killTotalTeam = 0;
            row3.forEach(player => {
                if (player.playerTeamID == row2.playerTeamID) {
                    killTotalTeam = killTotalTeam + player.kills;
                };
            });
            
            participation = Math.round((row2.kills / killTotalTeam) * 100);

            if (isNaN(participation)){
                participation = 0;
            }

            // Gets cs per minute
            csPerMinFloat = row2.totalCS / parseInt(row1.gameDurationMinutes.slice(0, -3));
            csPerMin = csPerMinFloat.toFixed(1);

            container.innerHTML += `
            <div style="background-color: #59343b; border-radius: 15px;" class="accordion-item" data-gameID="${row1.gameID}" id="matchCard">
                <div style="display: flex; background-color: #59343b; color: white;" class="accordion-header flex" onclick="toggleAccordion(this)">
                
                    <div class="nested-container">
                        <div style="border-radius: 15px; width: 35px; background-color: rgb(232, 64, 87);"></div>
                        <div class="item-container rankedGameCard">
                            <div class="innerCard">
                                <p class="match-card-text" style="color: #e8404b"><b>Ranked Solo</b></p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text">${row1.gameDate}</p>
                            </div>
                            <div class="lossDivider"></div>
                            <div class="innerCard">
                                <p class="match-card-text"><b>Defeat</b></p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text">${row1.gameDurationMinutes}</p>
                            </div>
                        </div>

                        <div class="item-container portraitCard">
                            <div class="innerCard">
                                
                                <div class="image-container">
                                    <img class="${row2.Champ}">
                                    <div class="text-over-image">${row2.champLevel}</div>
                                </div>
                                <div style="flex-direction: row;">
                                    <img class="${row2.summonerSpell1}">
                                    <img class="${row2.summonerSpell2}">
                                </div>
                            </div>
                        </div>


                        
                        <div style="padding-top: 5px;">
                            <div class="">
                                <img class="${itemToClass(row2.keystone)}">
                                <img class="${itemToClass(row2.secondaryRune)}">
                            </div>
                        </div>

                        <div style="padding-top: 5px;">
                            <div class="">
                                <img class="${itemToClass(row2.item0)}">
                                <img class="${itemToClass(row2.item1)}">
                                <img class="${itemToClass(row2.item2)}">
                            </div>
                        </div>
                        <div style="padding-top: 5px;">
                            <div class="">
                                <img class="${itemToClass(row2.item3)}">
                                <img class="${itemToClass(row2.item4)}">
                                <img class="${itemToClass(row2.item5)}">
                            </div>
                        </div>
                        <div style="padding-top: 5px;">
                            <div class="">
                                <img style="margin-top: 25px; border-radius: 50%;" class="${itemToClass(row2.item6)}">
                            </div>
                        </div>
                        

                        <div class="item-container px-2">
                            <div class="innerCard">
                                <p class="kda">${row2.kills} / <span style="color: #e84057">${row2.deaths}</span> / ${row2.assists}</p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text" style="color: #7c7e97; font-weight:400;">${kda}:1 KDA</p>
                            </div>
                            <div class="lossDivider"></div>
                            <div class="innerCard">
                                <p class="match-card-text" style="color: #e83d42"><b>K/P: ${participation}%</b></p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text">CS ${row2.totalCS} (${csPerMin})</p>
                            </div>
                            
                        </div>
                        
                        <div class="item-container teamCard">
                            <div class="innerCard">
                                <img class="${row3[0].Champ}Scoreboard">
                                <img class="${row3[1].Champ}Scoreboard">
                                <img class="${row3[2].Champ}Scoreboard">
                                <img class="${row3[3].Champ}Scoreboard">
                                <img class="${row3[4].Champ}Scoreboard">
                            </div>
                        </div>
                        <div class="item-container teamName">
                            <div class="innerCard">
                                <div>${player1Name}</div>
                                <div>${player2Name}</div>
                                <div>${player3Name}</div>
                                <div>${player4Name}</div>
                                <div>${player5Name}</div>
                            </div>
                        </div>

                        <div class="item-container teamCard ">
                            <div class="innerCard">
                                <img class="${row3[5].Champ}Scoreboard">
                                <img class="${row3[6].Champ}Scoreboard">
                                <img class="${row3[7].Champ}Scoreboard">
                                <img class="${row3[8].Champ}Scoreboard">
                                <img class="${row3[9].Champ}Scoreboard">
                            </div>
                        </div>
                        <div class="item-container teamName">
                            <div class="innerCard">
                                <div>${player6Name}</div>
                                <div>${player7Name}</div>
                                <div>${player8Name}</div>
                                <div>${player9Name}</div>
                                <div>${player10Name}</div>
                            </div>
                        </div>

                    </div>
                </div>

                
                
                
                <table class="accordion-body" style="color: white;">
                    <colgroup>
                        <col width="20%">
                        <col width="5%">
                        <col width="25%">
                        <col width="5%">
                        <col width="10%">
                        <col width="5%">
                        <col width="30%">
                    </colgroup>
                    <thead>
                        <tr style="text-align: center;">
                            <th colspan="3">Your Team</th>
                            <th>KDA</th>
                            <th>Damage</th>
                            <th>CS</th>
                            <th>Items</th>
                        </tr>
                    </thead>

                    <tbody id="${primaryTableID}">
                    </tbody>
                </table>
                
                <table class="accordion-body" style="color: white;">
                    <colgroup>
                        <col width="20%">
                        <col width="5%">
                        <col width="25%">
                        <col width="5%">
                        <col width="10%">
                        <col width="5%">
                        <col width="30%">
                    </colgroup>
                    <thead>
                        <tr style="text-align: center;">
                            <th colspan="3"><span class="result">Enemy Team</th>
                            <th>KDA</th>
                            <th>Damage</th>
                            <th>CS</th>
                            <th>Items</th>
                        </tr>
                    </thead>
                    
                    <tbody id="${secondaryTableID}">
                    </tbody>
                </table>

            </div>
            `;
          } 
        



        

        // Append the container to the data-container
        document.getElementById('data-container').appendChild(container);



        const primaryTable = document.getElementById(primaryTableID);
        const secondaryTable = document.getElementById(secondaryTableID);

        itemIndex = 0;
        if (row2.win === true) {
            winners.forEach(match =>{
                // Build the HTML content for each match object
                const winHTML = `
                    <tr result="WIN" class="overview-player overview-player--WIN css-1ya4cma e1i6zky90" style="text-align: center;">
                        <td>
                            <img class="innerScoreboard${match.Champ}">
                            <img class="${match.summonerSpell1}">
                            <img class="${match.summonerSpell2}">
                        </td>
                        <td>
                            ${match.champLevel}
                        </td>
                        <td class="innerScoreboardName">
                            ${match.riotID}
                        </td>
                        <td>
                            ${match.kills}/${match.deaths}/${match.assists}
                        </td>
                        <td>
                            ${match.goldEarned}
                        </td>
                        <td>
                            ${match.totalCS}
                        </td>
                        <td style="display: flex;">
                            <img class="${itemToClass(match.item0)}">
                            <img class="${itemToClass(match.item1)}">
                            <img class="${itemToClass(match.item2)}">
                            <img class="${itemToClass(match.item3)}">
                            <img class="${itemToClass(match.item4)}">
                            <img class="${itemToClass(match.item5)}">
                            <img class="${itemToClass(match.item6)}">
                        </td>
                    </tr>`;
                itemIndex = itemIndex + 1;
                // Append the HTML for the current match object to nested-container
                primaryTable.innerHTML += winHTML;
            });
            
            losers.forEach(match =>{

                // Build the HTML content for each match object
                const loseHTML = `
                <tr result="WIN" class="overview-player overview-player--WIN css-1ya4cma e1i6zky90" style="text-align: center;">
                    <td>
                        <img class="innerScoreboard${match.Champ}">
                        <img class="${match.summonerSpell1}">
                        <img class="${match.summonerSpell2}">
                    </td>
                    <td>
                        ${match.champLevel}
                    </td>
                    <td class="innerScoreboardName">
                        ${match.riotID}
                    </td>
                    <td>
                        ${match.kills}/${match.deaths}/${match.assists}
                    </td>
                    <td>
                        ${match.goldEarned}
                    </td>
                    <td>
                        ${match.totalCS}
                    </td>
                    <td style="display: flex;">
                        <img class="${itemToClass(match.item0)}">
                        <img class="${itemToClass(match.item1)}">
                        <img class="${itemToClass(match.item2)}">
                        <img class="${itemToClass(match.item3)}">
                        <img class="${itemToClass(match.item4)}">
                        <img class="${itemToClass(match.item5)}">
                        <img class="${itemToClass(match.item6)}">
                    </td>
                </tr>
                
                `;
                itemIndex = itemIndex + 1;
                // Append the HTML for the current match object to nested-container
                secondaryTable.innerHTML += loseHTML;
            });
        }
        else{
            losers.forEach(match =>{

                // Build the HTML content for each match object
                const loseHTML = `
                <tr result="WIN" class="overview-player overview-player--WIN css-1ya4cma e1i6zky90" style="text-align: center;">
                    <td>
                        <img class="innerScoreboard${match.Champ}">
                        <img class="${match.summonerSpell1}">
                        <img class="${match.summonerSpell2}">
                    </td>
                    <td>
                        ${match.champLevel}
                    </td>
                    <td class="innerScoreboardName">
                        ${match.riotID}
                    </td>
                    <td>
                        ${match.kills}/${match.deaths}/${match.assists}
                    </td>
                    <td>
                        ${match.goldEarned}
                    </td>
                    <td>
                        ${match.totalCS}
                    </td>
                    <td style="display: flex;">
                        <img class="${itemToClass(match.item0)}">
                        <img class="${itemToClass(match.item1)}">
                        <img class="${itemToClass(match.item2)}">
                        <img class="${itemToClass(match.item3)}">
                        <img class="${itemToClass(match.item4)}">
                        <img class="${itemToClass(match.item5)}">
                        <img class="${itemToClass(match.item6)}">
                    </td>
                </tr>
                `;
                itemIndex = itemIndex + 1;
                // Append the HTML for the current match object to nested-container
                primaryTable.innerHTML += loseHTML;
            });
            winners.forEach(match =>{

                // Build the HTML content for each match object
                const winHTML = `
                <tr result="WIN" class="overview-player overview-player--WIN css-1ya4cma e1i6zky90" style="text-align: center;">
                    <td>
                        <img class="innerScoreboard${match.Champ}">
                        <img class="${match.summonerSpell1}">
                        <img class="${match.summonerSpell2}">
                    </td>
                    <td>
                        ${match.champLevel}
                    </td>
                    <td class="innerScoreboardName">
                        ${match.riotID}
                    </td>
                    <td>
                        ${match.kills}/${match.deaths}/${match.assists}
                    </td>
                    <td>
                        ${match.goldEarned}
                    </td>
                    <td>
                        ${match.totalCS}
                    </td>
                    <td style="display: flex;">
                        <img class="${itemToClass(match.item0)}">
                        <img class="${itemToClass(match.item1)}">
                        <img class="${itemToClass(match.item2)}">
                        <img class="${itemToClass(match.item3)}">
                        <img class="${itemToClass(match.item4)}">
                        <img class="${itemToClass(match.item5)}">
                        <img class="${itemToClass(match.item6)}">
                    </td>
                </tr>
                `;
                itemIndex = itemIndex + 1;
                // Append the HTML for the current match object to nested-container
                secondaryTable.innerHTML += winHTML;
            });
        }
        cardCount = cardCount + 1;
    });
    
    
    showMoreButtonDiv = document.getElementById('showMoreButtonDiv')
    showMoreButtonDiv.innerHTML = `<button id="showMoreButtonTag" class="center searchSection text-dark text-center fw-bold" style="border-radius: 15px; font-family: VCR OSD Mono, sans-serif; font-size: 150%; width: 740px; display: flex; justify-content: center;" onclick="showMore()">SHOW MORE</button>`;

    
    
}