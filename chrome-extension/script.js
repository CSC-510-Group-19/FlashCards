var localId = ''
const readFromIndexedDB = async (dbName, storeName) => {
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
  };
async function invokeAPI() {
    /* if (!localId) {
        console.error('localId is not set');
        return;
    } */
    // const url = `http://127.0.0.1:5000/deck/all?localId=${localId};`
    const url = `http://127.0.0.1:5000/deck/all`;
    const response = await fetch(`http://127.0.0.1:5000/deck/all?localId=${localId}`, {
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

    console.log("Chosen deckId is " + chosenDeckId);
    console.log("Front text is " + frontText);
    console.log("Back text is " + backText);
    console.log("Hint text is " + hintText);
}
invokeAPI()
// No need to call getLocalId() here