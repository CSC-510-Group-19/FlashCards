async function invokeAPI() {
    const url = `http://127.0.0.1:5000/deck/all`;
    const response = await fetch(`http://127.0.0.1:5000/deck/all`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        mode: 'cors',
    });
    if (!response.ok) {
        throw new Error('Network response was not ok '+response);
    }
    const data = await response.json();
    console.log('API Response:', data);

    const deckList = data.decks;
    const deckContainer = document.getElementById('deckContainer');
    deckContainer.innerHTML = '';

    deckList.forEach(deck => {
        const deckDiv = document.createElement('div');
        const label = document.createElement('label');
        label.textContent = deck.description;
        const input = document.createElement('input');
        input.type = 'radio';
        input.name = "deckId";
        input.value = deck.id;
        input.id = deck.id;
        deckDiv.appendChild(input);
        deckDiv.appendChild(label);
        deckContainer.appendChild(deckDiv);
    });

    const form = document.getElementById('form');
    if (form) {
        const submissionMessage = document.querySelector('#submission-message');
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            addCard();
            submissionMessage.classList.add('show');
        });
    } else {
        console.error('Form not found!');
    }
}

function addCard() {
    const radioGroup = document.getElementsByName("deckId");
    const chosenDeckId = Array.from(radioGroup).find(radio => radio.checked)?.value;
    const frontText = document.getElementById("front").value;
    const backText = document.getElementById("back").value;
    const hintText = document.getElementById("hint").value;

    data = {
        cards:
        [
            {
                'front': frontText,
                'back': backText,
                'hint': hintText
            }
        ]
    }
    fetch(`http://127.0.0.1:5000/deck/` + chosenDeckId + `/public/card/create`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(responseData => {
        console.log('Success:', responseData);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
invokeAPI()