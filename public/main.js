window.onload = function() {
    const displayArea = document.getElementById('display');
    const bookSelect = document.getElementById('book');
    const chapterSelect = document.getElementById('chapter');
    const verseSelect = document.getElementById('verse');
    const popup = document.getElementById('popup');

    // Load books into the dropdown
    for (const book in books) {
        let option = document.createElement("option");
        option.value = book;
        option.text = book;
        bookSelect.appendChild(option);
    }

    // Load chapters based on selected book
    bookSelect.onchange = function() {
        updateChapters();
    };

    // Load verses based on selected chapter
    chapterSelect.onchange = function() {
        updateVerses();
    };

    // Display selected verse
    verseSelect.onchange = function() {
        displayVerse();
    };

    function updateChapters() {
        const selectedBook = bookSelect.value;
        chapterSelect.innerHTML = ""; // Clear chapters
        if (books[selectedBook]) {
            const chapters = books[selectedBook].split(" ");
            chapters.forEach((_, index) => {
                let option = document.createElement("option");
                option.value = index + 1;
                option.text = `Chapter ${index + 1}`;
                chapterSelect.appendChild(option);
            });
            updateVerses();
        }
    }

    function updateVerses() {
        const selectedBook = bookSelect.value;
        const selectedChapter = chapterSelect.value - 1;
        verseSelect.innerHTML = ""; // Clear verses
        const chapters = books[selectedBook].split(" ");
        const verseCount = chapters[selectedChapter];

        for (let i = 1; i <= verseCount; i++) {
            let option = document.createElement("option");
            option.value = i;
            option.text = `Verse ${i}`;
            verseSelect.appendChild(option);
        }
        displayVerse();
    }

    function displayVerse() {
        const selectedBook = bookSelect.value;
        const selectedChapter = parseInt(chapterSelect.value);
        const selectedVerse = parseInt(verseSelect.value);

        // Load and display the verse
        loadVerse(selectedBook, selectedChapter, selectedVerse, displayArea);
    }

    // Function to load and render verse with overlays
    function loadVerse(book, chapter, verse, displayElement) {
        getVerseData(book, chapter, verse)
            .then(verseData => {
                if (verseData) {
                    // Use VerseMarkupHorizontal or VerseMarkupVertical for rendering
                    const verseElement = verseMarkupHorizontal(verseData, false);
                    displayElement.innerHTML = ""; // Clear previous verse
                    displayElement.appendChild(verseElement);

                    // Add hover effect for showing lemma and morphology in the popup overlay
                    displayElement.querySelectorAll(".Hebrew").forEach(wordElement => {
                        wordElement.onmouseover = function(event) {
                            const lemma = wordElement.getAttribute("data-lemma");
                            const morphology = wordElement.getAttribute("data-morph");
                            showPopup(event, lemma, morphology);
                        };
                        wordElement.onmouseout = hidePopup;
                    });
                }
            })
            .catch(error => console.error("Error loading verse data:", error));
    }

    // Show popup overlay with lemma and morphology
    function showPopup(event, lemma, morphology) {
        popup.innerHTML = `<strong>Lemma:</strong> ${lemma}<br><strong>Morphology:</strong> ${morphology}`;
        popup.style.display = "block";
        popup.style.top = `${event.pageY + 10}px`;
        popup.style.left = `${event.pageX + 10}px`;
    }

    function hidePopup() {
        popup.style.display = "none";
    }

    // Function to fetch verse data from JSON file
    function getVerseData(book, chapter, verse) {
        // Convert book name to lowercase and construct file path directly
        const filePath = `../json/hebrew/${book.toLowerCase()}.json`;
    
        return fetch(filePath)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Failed to load file: " + filePath);
                }
                return response.json();
            })
            .then(data => {
                // Assuming the JSON is structured by chapter and verse (adjust if necessary)
                return data[chapter - 1][verse - 1]; // Adjust based on actual JSON structure
            })
            .catch(error => console.error("Error loading verse data:", error));
    }
};