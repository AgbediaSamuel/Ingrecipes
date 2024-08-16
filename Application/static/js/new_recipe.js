// Add an event listener to the button to trigger the fetch request
document.querySelector('.recipe-submit-btn').addEventListener('click', function() {
    const userInput = document.querySelector('.recipe-input-field').value;

    fetch('/api/get_recipes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ingredients: userInput })
    })
    .then(response => response.json())
    .then(data => {
        const recipeContainer = document.querySelector('.recipe-results'); // Assuming there's a container for recipes
        recipeContainer.innerHTML = ''; // Clear previous results

        if (data.error) {
            recipeContainer.innerHTML = `<p>Error: ${data.error}</p>`;
            return;
        }

        data.forEach(recipe => {
            const recipeElement = document.createElement('div');
            recipeElement.classList.add('recipe-item');

            recipeElement.innerHTML = `
                <h3>${recipe.title}</h3>
                <img src="${recipe.image}" alt="${recipe.title}" />
                <a href="${recipe.url}" target="_blank">View Recipe</a>
            `;

            recipeContainer.appendChild(recipeElement);
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
