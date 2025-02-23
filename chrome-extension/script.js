/*const readFromIndexedDB = async (dbName, storeName) => {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open("FlashcardsDB");
  
      request.onsuccess = (event) => {
        const db = event.target.result;
        const transaction = db.transaction("Flashcards", 'readonly');
        const store = transaction.objectStore("Flashcards");
        localId = store.getAll() || 'dWc0jg2imjXGVAUKb07n2YYgj273';
  
        dataRequest.onsuccess = () => {
          resolve(dataRequest.result);
        };
  
        dataRequest.onerror = () => {
          reject('Error reading data from IndexedDB');
        };
      };
  
      request.onerror = () => {
        reject('Error opening IndexedDB');
      };
    });
  }; */
/* window.addEventListener('message', (event) => {
    // Ensure the message is from a trusted source
    if (event.data.type === 'TO_EXTENSION') {
      const { type, payload } = event.data;
  
      // Relay the message to the background script
      localId = payload;
    }
});*/
async function invokeAPI() {
    /* if (!localId) {
        console.error('localId is not set');
        return;
    } */
    // const url = `http://127.0.0.1:5000/deck/all?localId=${localId};`
    const url = `http://127.0.0.1:5000/deck/all`;
    const response = await fetch(`http://127.0.0.1:5000/deck/all`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        mode: 'cors', // Ensure CORS mode is enabled
    });
    if (!response.ok) {
        throw new Error('Network response was not ok '+response);
    }
    const data = await response.json();
    console.log('API Response:', data);

    const deckList = data.decks;
    const deckContainer = document.getElementById('deckContainer');
    deckContainer.innerHTML = '';

    // Populate the deck container with radio buttons for each deck
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

    // Attach the event listener to the form
    const form = document.getElementById('form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            addCard();
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
// No need to call getLocalId() here