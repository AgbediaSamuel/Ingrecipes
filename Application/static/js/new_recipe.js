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
        const recipeContainer = document.querySelector('.recipe-results');
        recipeContainer.innerHTML = '';

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
                <button class="save-recipe-btn" data-title="${recipe.title}" data-url="${recipe.url}">Save Recipe</button>
            `;

            recipeContainer.appendChild(recipeElement);
        });

        // Add event listeners to "Save Recipe" buttons
        document.querySelectorAll('.save-recipe-btn').forEach(button => {
            button.addEventListener('click', function() {
                const title = this.getAttribute('data-title');
                const url = this.getAttribute('data-url');

                // Using DOM Manipulation to get information that needs to be saved
                document.getElementById('recipe-title').value = title;
                document.getElementById('recipe-url').value = url;
                document.getElementById('save-recipe-form').submit();
            });
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
