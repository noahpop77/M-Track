async function summonerSearch() {
    var url = "http://10.0.0.150/summonerSearch";

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
        printMatches(data.gameData, data.playerStats, data.matchData, summonerName);
    })
    .catch(function(error) {
        responseParagraph.textContent = error.message;
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
        printMatches(data.gameData, data.playerStats, data.matchData, summonerName);
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


async function printMatches(gameDataIn, playerStatsIn, matchData, summonerName) {
    // Assuming gameData and playerStats are available as arrays of objects
    const gameData = gameDataIn;
    const playerStats = playerStatsIn;

    var responseParagraph = document.getElementById('responseParagraph');
    responseParagraph.textContent = summonerName;


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
        
        if (row2.win == true && row2.sumName.toLowerCase() == summonerName.toLowerCase()) {

            getChampIcon(row2.Champ, accordionChampId);
            sum1 = getSummonerIcon(row2.summonerSpell1, summoner1ID);
            sum2 = getSummonerIcon(row2.summonerSpell2, summoner2ID);
            kda = calculateKDA(row2.kills, row2.deaths, row2.assists)

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
                                    <img id="${accordionChampId}" alt="champIcon" style="height: 56px; width: 56px; border-radius: 15%;">
                                    <div class="text-over-image">${row2.champLevel}</div>
                                </div>
                                <div style="flex-direction: row;">
                                    <img id="${summoner1ID}" alt="summoner1" class="summonerIcons">
                                    <img id="${summoner2ID}" alt="summoner2" class="summonerIcons">
                                </div>
                            </div>
                        </div>

                        <div class="item-container px-2">
                            <div class="innerCard">
                                <p class="kda">${row2.kills}/${row2.deaths}/${row2.assists}</p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text">${kda}:1 KDA</p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text">${row2.champLevel}</p>
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
            
            container.innerHTML = `
            <div style="background-color: #59343b;" class="accordion-item">
                <div style="display: flex; background-color: #59343b; color: white;" class="accordion-header flex" onclick="toggleAccordion(this)">
                
                    <div class="nested-container">
                        <div class="item-container" style="width:108px;">
                            <div class="innerCard">
                                <p class="match-card-text" style="color: #e8404b">Ranked Solo</p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text">${row1.gameDate}</p>
                            </div>
                            <div class="lossDivider"></div>
                            <div class="innerCard">
                                <p class="match-card-text">Defeat</p>
                            </div>
                            <div class="innerCard">
                                <p class="match-card-text">${row1.gameDurationMinutes}</p>
                            </div>
                        </div>
                        <div class="item-container">
                            <div class="innerCard">
                                <img id="${accordionChampId}" alt="champIcon" style="height: 56px; width: 56px; border-radius: 15%;">
                                <div style="flex-direction: row;">
                                    <img id="${summoner1ID}" alt="summoner1" class="summonerIcons">
                                    <img id="${summoner2ID}" alt="summoner2" class="summonerIcons">
                                </div>
                            </div>

                        </div>
                        <div class="item-container">
                            <div class="item-container">
                                <p class="match-card-text">${row2.kills}/${row2.deaths}/${row2.assists}</p>
                            </div>
                            <div class="item-container">
                                <p class="match-card-text">${row2.champLevel}</p>
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

        // ${match.playerTeamID}
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