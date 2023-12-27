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


function toggleAccordion(header) {
    // Get the parent accordion item
    var accordionItem = header.parentNode;

    // Toggle the "active" class to show/hide the accordion body
    accordionItem.classList.toggle("active");
}


async function sendPostRequest() {
    var url = "http://10.0.0.150/getHistory";

    var responseParagraph = document.getElementById('responseParagraph');
    responseParagraph.textContent = "Getting history...";
    var summonerName = document.getElementById("nameInput").value;
    console.log("summonerName: " + summonerName)
    console.log("Updating Name:", summonerName);
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
        console.log("PRE PRINTING TO SCREEN");
        // location.reload();
        printMatches(data.gameData, data.playerStats, data.matchData, summonerName);
        // responseParagraph.textContent = answer;
        console.log("Data rewritten to screen");
    })
    .catch(function(error) {
        responseParagraph.textContent = error.message; // Display error message
    });
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
        // console.log(row2)
        // Create a new div element
        const container = document.createElement('div');
        container.classList.add('px-5');



        const accordionBodyId = `matchData_${index}`;

        
        if (row2.win == true && row2.sumName == summonerName) {
            container.innerHTML = `
            <div style="background-color: #28658b;" class="accordion-item">
                <div style="display: flex; background-color: #28658b; color: white;" class="accordion-header" onclick="toggleAccordion(this)">
                
                    <div class="nested-container">
                        <div class="item-container">
                            <p class="match-card-text">${row1.gameID}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.champLevel}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.kills}/${row2.deaths}/${row2.assists}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.Champ}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.sumName}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.playerTeamID}</p>
                        </div>
                    </div>

                    <div id="nested2" class="nested-container">
                        <div class="item-container">
                            <p class="match-card-text">${row1.gameID}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.champLevel}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.kills}/${row2.deaths}/${row2.assists}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.Champ}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.sumName}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.playerTeamID}</p>
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
            // Build the HTML content inside the div
            container.innerHTML = `
            <div style="background-color: #59343b;" class="accordion-item">
                <div style="display: flex; background-color: #59343b; color: white;" class="accordion-header" onclick="toggleAccordion(this)">
                
                    <div class="nested-container">
                        <div class="item-container">
                            <p class="match-card-text">${row1.gameID}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.champLevel}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.kills}/${row2.deaths}/${row2.assists}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.Champ}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.sumName}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.playerTeamID}</p>
                        </div>
                    </div>

                    <div id="nested2" class="nested-container">
                        <div class="item-container">
                            <p class="match-card-text">${row1.gameID}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.champLevel}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.kills}/${row2.deaths}/${row2.assists}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.Champ}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.sumName}</p>
                        </div>
                        <div class="item-container">
                            <p class="match-card-text">${row2.playerTeamID}</p>
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