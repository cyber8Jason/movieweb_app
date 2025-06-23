async function searchMovie() {
    const searchInput = document.getElementById('movieSearch');
    const resultsDiv = document.getElementById('searchResults');
    const title = searchInput.value.trim();

    if (!title) {
        resultsDiv.innerHTML = '<p class="error">Please enter a movie title</p>';
        return;
    }

    try {
        const response = await fetch(`/api/search_movie?title=${encodeURIComponent(title)}`);
        const data = await response.json();

        if (response.ok && data) {
            // Fill form fields
            document.getElementById('name').value = data.title || '';
            document.getElementById('director').value = data.director || '';
            document.getElementById('year').value = data.year || '';
            document.getElementById('rating').value = data.rating || '';
            document.getElementById('poster').value = data.poster || '';

            // Show search results with movie cover
            resultsDiv.innerHTML = `
                <div class="movie-result">
                    <div class="movie-poster">
                        <img src="${data.poster !== 'N/A' ? data.poster : '/static/images/no-poster.jpg'}"
                             alt="${data.title} poster">
                    </div>
                    <div class="movie-info">
                        <h3>${data.title}</h3>
                        <p>Director: ${data.director}</p>
                        <p>Year: ${data.year}</p>
                        <p>Rating: ${data.rating}/10</p>
                    </div>
                </div>`;
        } else {
            resultsDiv.innerHTML = '<p class="error">Movie not found</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = '<p class="error">An error occurred during the search</p>';
    }
}
