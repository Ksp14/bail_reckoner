document.getElementById('bail-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const prisonerId = document.getElementById('prisoner_id').value;
    
    // Ensure the prisoner ID is provided
    if (prisonerId === "") {
        alert("Please enter a prisoner ID.");
        return;
    }

    // Send the POST request to the Flask backend
    fetch('/api/bail', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prisoner_id: prisonerId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('result').innerHTML = `<span style="color: red;">${data.error}</span>`;
        } else {
            document.getElementById('result').innerHTML = `<span>${data.report}</span>`;
        }
    })
    .catch(error => {
        document.getElementById('result').innerHTML = `<span style="color: red;">Error fetching data</span>`;
        console.error('Error:', error);
    });
});
