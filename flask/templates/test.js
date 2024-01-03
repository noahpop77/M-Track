async function getImage(champName) {

    var url = "http://10.0.0.150/getIcon";

    await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: champName
    })
    
    .then(function(response) {
        // Check if the response was successful
        if (response.ok) {
            console.log(response.blob());
            const blob = response.blob();
            const image =  URL.createObjectURL(blob); // Convert response to text
            document.getElementById('mainIcon').src = image;
        } else {
            throw new Error('Error: ' + response.status); // Throw an error
        }
    })
    .catch(function(error) {
        console.log(error.message);
            // Display error message
    });
}
