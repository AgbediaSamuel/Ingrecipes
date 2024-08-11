document.querySelector('.recipe-submit-btn').addEventListener('click', function() {
    const userInput = document.querySelector('.recipe-input-field').value;

    fetch('/get_recipes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ingredients: userInput })
    })
    .then(response => response.json())
    .then(data => {

        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
