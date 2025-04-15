# Firebase setup
To set up the backend you must first create a firebase account at firebase.google.com.
Enable realtime database
Under rules, apply the following:
```
{
  "rules": {
    "deck" : {
        ".indexOn": ["userId", "deckId", "visibility", "title"]
    },
    "folder": {
      ".indexOn": ["userId"]
    },
    "folder_deck": {
      ".indexOn": ["deckId", "folderId"]
    },
    "card":  {
      ".indexOn": ["Id", "deckId"]
    },
    ".read": true,
    ".write": true
	}
}
```

Get the firebaseConfig JSON Object from the firebase console, click the gear beside Project Overview -> Project settings.
Replace firebaseConfig with your values in backend/src/__init__.py and frontend/src/initializeFirebase.tsx

In firebase console, click Authentication, then User sign-in method. enable Google, Facebook, and github. You will need to create accounts with these respective organizations. Instructions for this can be found in the firebase documentation.
