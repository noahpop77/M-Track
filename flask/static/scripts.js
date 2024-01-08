async function summonerSearch() {
    var url = "http://10.0.0.150/summonerSearch";

    var responseParagraph = document.getElementById('responseParagraph');
    responseParagraph.textContent = "Searching for Summoner...";
    var summonerName = document.getElementById("nameInput").value;

    await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: summonerName
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
        printMatches(data.gameData, data.playerStats, data.matchData, data.summonerName);
    })
    .catch(function(error) {
        responseParagraph.textContent = "Summoner not found..."
        console.log(error)
        //responseParagraph.textContent = error.message;
            // Display error message
    });
}



async function updateData() {
    var url = "http://10.0.0.150/getHistory";

    var responseParagraph = document.getElementById('responseParagraph');
    responseParagraph.textContent = "Getting history...";
    var summonerName = document.getElementById("nameInput").value;

    await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: summonerName
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
        //responseParagraph.textContent = "Updated, Please Refresh";
        printMatches(data.gameData, data.playerStats, data.matchData, data.summonerName);
    })
    .catch(function(error) {
        responseParagraph.textContent = error.message; // Display error message
    });
}


function toggleAccordion(header) {
    // Get the parent accordion item
    var accordionItem = header.parentNode;
    // Toggle the "active" class to show/hide the accordion body
    accordionItem.classList.toggle("active");
}





async function getItemIcon(itemName, elementID) {
    if (itemName === "N/A") {
        itemName = "NA"
    }
    var url = "http://10.0.0.150/getItemIcon";

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: itemName
        });

        // Check if the response was successful
        if (response.ok) {
            const blob = await response.blob(); // Await the blob Promise
            const image = URL.createObjectURL(blob);
            document.getElementById(elementID).src = image;
        } else {
            throw new Error('Error: ' + response.status); // Throw an error
        }
    } catch (error) {
        // Display error message
        console.log(error.message);
    }
}

async function getChampIcon(champName, elementID) {
    var url = "http://10.0.0.150/getChampIcon";

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: champName
        });

        // Check if the response was successful
        if (response.ok) {
            const blob = await response.blob(); // Await the blob Promise
            const image = URL.createObjectURL(blob);
            document.getElementById(elementID).src = image;
        } else {
            throw new Error('Error: ' + response.status); // Throw an error
        }
    } catch (error) {
        // Display error message
        console.log(error.message);
    }
}

async function getSummonerIcon(summoner, elementID) {
    var url = "http://10.0.0.150/getSummoners";

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: summoner
        });

        // Check if the response was successful
        if (response.ok) {
            const blob = await response.blob(); // Await the blob Promise
            const image = URL.createObjectURL(blob);
            document.getElementById(elementID).src = image;
        } else {
            throw new Error('Error: ' + response.status); // Throw an error
        }
    } catch (error) {
        console.log(error.message);
        // Display error message
    }
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
                <button id="updateButton" class="btn btn-dark btn-sm rounded-3" style="height: 100%; font-weight:bold; font-size: 50%; font-family: VCR OSD Mono, sans-serif; outline: none; box-shadow: none; padding: 7px;" onclick="updateData()">Update</button>
                </div>
                <div class="col-8 d-flex justify-content-center align-items-center">
                <h3 class="mb-3 mb-md-0 fw-bold" style="font-family: VCR OSD Mono, sans-serif; font-size: 100%;">${summonerName}</h3>
            </div>
            <div class="col-2"></div>
        </div>
    </div>
    `;

    // Get the data-container element
    const dataContainer = document.getElementById('data-container');
    // Clear existing content in the data-container
    dataContainer.innerHTML = '';


    // Loop through the arrays simultaneously using forEach
    gameData.forEach((row1, index) => {

        const row2 = playerStats[index];
        const row3 = matchData[index];
        
        // Create a new div element
        const container = document.createElement('div');
        container.classList.add('px-5');


        const accordionBodyId = `matchData_${index}`;
        const accordionChampId = `champPic_${index}`;
        const summoner1ID = `summoner1_${index}`;
        const summoner2ID = `summoner2_${index}`;

        const item0ID = `item0ID_${index}`;
        const item1ID = `item1ID_${index}`;
        const item2ID = `item2ID_${index}`;
        const item3ID = `item3ID_${index}`;
        const item4ID = `item4ID_${index}`;
        const item5ID = `item5ID_${index}`;
        const item6ID = `item6ID_${index}`;

        const playerIcon1ID = `playerIcon1ID_${index}`;
        const playerIcon2ID = `playerIcon2ID_${index}`;
        const playerIcon3ID = `playerIcon3ID_${index}`;
        const playerIcon4ID = `playerIcon4ID_${index}`;
        const playerIcon5ID = `playerIcon5ID_${index}`;
        const playerIcon6ID = `playerIcon6ID_${index}`;
        const playerIcon7ID = `playerIcon7ID_${index}`;
        const playerIcon8ID = `playerIcon8ID_${index}`;
        const playerIcon9ID = `playerIcon9ID_${index}`;
        const playerIcon10ID = `playerIcon10ID_${index}`;
        
        if (row2.win == true && row2.sumName.toLowerCase() == summonerName.toLowerCase()) {
            
            getChampIcon(row2.Champ, accordionChampId);
            sum1 = getSummonerIcon(row2.summonerSpell1, summoner1ID);
            sum2 = getSummonerIcon(row2.summonerSpell2, summoner2ID);
            kda = calculateKDA(row2.kills, row2.deaths, row2.assists);
            item0 = getItemIcon(row2.item0, item0ID);
            item1 = getItemIcon(row2.item1, item1ID);
            item2 = getItemIcon(row2.item2, item2ID);
            item3 = getItemIcon(row2.item3, item3ID);
            item4 = getItemIcon(row2.item4, item4ID);
            item5 = getItemIcon(row2.item5, item5ID);
            item6 = getItemIcon(row2.item6, item6ID);

            player1 = getChampIcon(row3[0].Champ, playerIcon1ID);
            player2 = getChampIcon(row3[1].Champ, playerIcon2ID);
            player3 = getChampIcon(row3[2].Champ, playerIcon3ID);
            player4 = getChampIcon(row3[3].Champ, playerIcon4ID);
            player5 = getChampIcon(row3[4].Champ, playerIcon5ID);
            player6 = getChampIcon(row3[5].Champ, playerIcon6ID);
            player7 = getChampIcon(row3[6].Champ, playerIcon7ID);
            player8 = getChampIcon(row3[7].Champ, playerIcon8ID);
            player9 = getChampIcon(row3[8].Champ, playerIcon9ID);
            player10 = getChampIcon(row3[9].Champ, playerIcon10ID);

            player1Name = row3[0].sumName;
            player2Name = row3[1].sumName;
            player3Name = row3[2].sumName; 
            player4Name = row3[3].sumName; 
            player5Name = row3[4].sumName; 
            player6Name = row3[5].sumName; 
            player7Name = row3[6].sumName; 
            player8Name = row3[7].sumName; 
            player9Name = row3[8].sumName; 
            player10Name = row3[9].sumName;

            //Gets the Kill participation
            var killTotalTeam = 0;
            row3.forEach(player => {
                if (player.playerTeamID == row2.playerTeamID) {
                    killTotalTeam = killTotalTeam + player.kills;
                };
            });
            participation = Math.round((row2.kills / killTotalTeam) * 100);

            // Gets cs per minute
            csPerMinFloat = row2.totalCS / parseInt(row1.gameDurationMinutes.slice(0, -3));
            csPerMin = csPerMinFloat.toFixed(1);
            container.innerHTML = `
            <div style="background-color: #28344e;" class="accordion-item">
                <div style="display: flex; background-color: #28344e; color: white;" class="accordion-header flex" onclick="toggleAccordion(this)">
                
                    <div class="nested-container">
                        <div class="item-container rankedGameCard">
                            <div class="innerCard">
                                <p class="match-card-text" style="color: #336be3"><b>Ranked Solo</b></p>
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
                                    <img class="champIcon" id="${accordionChampId}" alt="champIcon">
                                    <div class="text-over-image">${row2.champLevel}</div>
                                </div>
                                <div style="flex-direction: row;">
                                    <img id="${summoner1ID}" alt="summoner1" class="summonerIcons">
                                    <img id="${summoner2ID}" alt="summoner2" class="summonerIcons">
                                </div>
                            </div>
                        </div>


                        <div class="item-container itemCard">
                            <div class="innerCard">
                                <img id="${item0ID}" alt="summoner1" class="summonerIcons">
                                <img id="${item1ID}" alt="summoner1" class="summonerIcons">
                                <img id="${item2ID}" alt="summoner1" class="summonerIcons">
                            </div>
                        </div>
                        <div class="item-container itemCard">
                            <div class="innerCard">
                                <img id="${item3ID}" alt="summoner1" class="summonerIcons">
                                <img id="${item4ID}" alt="summoner1" class="summonerIcons">
                                <img id="${item5ID}" alt="summoner1" class="summonerIcons">
                            </div>
                        </div>
                        <div class="item-container itemCard">
                            <div class="innerCard">
                                <img id="${item6ID}" style="margin-top: 56px; border-radius: 50%;" alt="summoner1" class="summonerIcons">
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
                                <img id="${playerIcon1ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon2ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon3ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon4ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon5ID}" alt="summoner1" class="teamIcon">
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
                                <img id="${playerIcon6ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon7ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon8ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon9ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon10ID}" alt="summoner1" class="teamIcon">
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
                

                <table result="WIN" class="accordion-body" style="color: white;">
                    <colgroup>
                        <col width="44">
                        <col width="18">
                        <col width="18">
                        <col>
                        <col width="68">
                        <col width="98">
                        <col width="120">
                        <col width="48">
                        <col width="56">
                        <col width="175">
                    </colgroup>
                    <thead>
                        <tr style="text-align: center;">
                            <th colspan="3"><span class="result">Victory</span>(Blue Team)</th>
                            <th>KDA</th>
                            <th>Damage</th>
                            <th>CS</th>
                            <th>Item</th>
                            <th>Win/Lose</th>
                            <th>${row1.gameID}</th>
                        </tr>
                    </thead>

                    <tbody id="${accordionBodyId}">
                    </tbody>

                </table>
            </div>
            `;
          } 


          else {
            getChampIcon(row2.Champ, accordionChampId);
            sum1 = getSummonerIcon(row2.summonerSpell1, summoner1ID);
            sum2 = getSummonerIcon(row2.summonerSpell2, summoner2ID);

            kda = calculateKDA(row2.kills, row2.deaths, row2.assists);

            item0 = getItemIcon(row2.item0, item0ID);
            item1 = getItemIcon(row2.item1, item1ID);
            item2 = getItemIcon(row2.item2, item2ID);
            item3 = getItemIcon(row2.item3, item3ID);
            item4 = getItemIcon(row2.item4, item4ID);
            item5 = getItemIcon(row2.item5, item5ID);
            item6 = getItemIcon(row2.item6, item6ID);

            player1 = getChampIcon(row3[0].Champ, playerIcon1ID);
            player2 = getChampIcon(row3[1].Champ, playerIcon2ID);
            player3 = getChampIcon(row3[2].Champ, playerIcon3ID);
            player4 = getChampIcon(row3[3].Champ, playerIcon4ID);
            player5 = getChampIcon(row3[4].Champ, playerIcon5ID);
            player6 = getChampIcon(row3[5].Champ, playerIcon6ID);
            player7 = getChampIcon(row3[6].Champ, playerIcon7ID);
            player8 = getChampIcon(row3[7].Champ, playerIcon8ID);
            player9 = getChampIcon(row3[8].Champ, playerIcon9ID);
            player10 = getChampIcon(row3[9].Champ, playerIcon10ID);

            player1Name = row3[0].sumName;
            player2Name = row3[1].sumName;
            player3Name = row3[2].sumName; 
            player4Name = row3[3].sumName; 
            player5Name = row3[4].sumName; 
            player6Name = row3[5].sumName; 
            player7Name = row3[6].sumName; 
            player8Name = row3[7].sumName; 
            player9Name = row3[8].sumName; 
            player10Name = row3[9].sumName;

            //Gets the Kill participation
            var killTotalTeam = 0;
            row3.forEach(player => {
                if (player.playerTeamID == row2.playerTeamID) {
                    killTotalTeam = killTotalTeam + player.kills;
                };
            });
            participation = Math.round((row2.kills / killTotalTeam) * 100);

            // Gets cs per minute
            csPerMinFloat = row2.totalCS / parseInt(row1.gameDurationMinutes.slice(0, -3));
            csPerMin = csPerMinFloat.toFixed(1);

            container.innerHTML = `
            <div style="background-color: #59343b;" class="accordion-item">
                <div style="display: flex; background-color: #59343b; color: white;" class="accordion-header flex" onclick="toggleAccordion(this)">
                
                    <div class="nested-container">
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
                                    <img class="champIcon" id="${accordionChampId}" alt="champIcon">
                                    <div class="text-over-image">${row2.champLevel}</div>
                                </div>
                                <div style="flex-direction: row;">
                                    <img id="${summoner1ID}" alt="summoner1" class="summonerIcons">
                                    <img id="${summoner2ID}" alt="summoner2" class="summonerIcons">
                                </div>
                            </div>
                        </div>


                        <div class="item-container itemCard">
                            <div class="innerCard">
                                <img id="${item0ID}" alt="summoner1" class="summonerIcons">
                                <img id="${item1ID}" alt="summoner1" class="summonerIcons">
                                <img id="${item2ID}" alt="summoner1" class="summonerIcons">
                            </div>
                        </div>
                        <div class="item-container itemCard">
                            <div class="innerCard">
                                <img id="${item3ID}" alt="summoner1" class="summonerIcons">
                                <img id="${item4ID}" alt="summoner1" class="summonerIcons">
                                <img id="${item5ID}" alt="summoner1" class="summonerIcons">
                            </div>
                        </div>
                        <div class="item-container itemCard">
                            <div class="innerCard">
                                <img id="${item6ID}" style="margin-top: 56px; border-radius: 50%;" alt="summoner1" class="summonerIcons">
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
                                <img id="${playerIcon1ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon2ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon3ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon4ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon5ID}" alt="summoner1" class="teamIcon">
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
                                <img id="${playerIcon6ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon7ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon8ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon9ID}" alt="summoner1" class="teamIcon">
                                <img id="${playerIcon10ID}" alt="summoner1" class="teamIcon">
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
                

                <table result="WIN" class="accordion-body" style="color: white;">
                    <colgroup>
                        <col width="44">
                        <col width="18">
                        <col width="18">
                        <col>
                        <col width="68">
                        <col width="98">
                        <col width="120">
                        <col width="48">
                        <col width="56">
                        <col width="175">
                    </colgroup>
                    <thead>
                        <tr style="text-align: center;">
                            <th colspan="3"><span class="result">Victory</span>(Blue Team)</th>
                            <th>KDA</th>
                            <th>Damage</th>
                            <th>CS</th>
                            <th>Item</th>
                            <th>Win/Lose</th>
                            <th>${row1.gameID}</th>
                        </tr>
                    </thead>

                    <tbody id="${accordionBodyId}">
                    </tbody>

                </table>
            </div>
            `;
          } 
        



        // Append the container to the data-container
        document.getElementById('data-container').appendChild(container);


        const accordionBody = document.getElementById(accordionBodyId);


        // Loop through matchData and display 10 objects per element inside nested-container
        row3.forEach(match => {
            // Build the HTML content for each match object
            const matchHTML = `
                <tr result="WIN" class="overview-player overview-player--WIN css-1ya4cma e1i6zky90" style="text-align: center;">
                    <td class="champion">
                        ${match.Champ}
                    </td>
                    <td class="spells">
                        ${match.champLevel}
                    </td><td class="champion">
                        ${match.sumName}
                    </td>
                    <td class="champion">
                        ${match.kills}/${match.deaths}/${match.assists}
                    </td>
                    <td class="spells">
                        ${match.goldEarned}
                    </td>
                    <td class="spells">
                        999 cs
                    </td>
                    <td class="champion">
                        Maw
                    </td>
                    <td class="champion">
                        ${match.win}
                    </td>
                </tr>
            `;

            // Append the HTML for the current match object to nested-container
            accordionBody.innerHTML += matchHTML;
        });
        

    });
}