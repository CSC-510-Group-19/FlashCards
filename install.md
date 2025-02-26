## Features:

1. Login and Sign up - Hosted on [Firebase](https://firebase.google.com/)
                                         
2. Based on Python-Flask

## Requirements:

```pip install pyrebase4```

```pip install flask ```

# Test the Project:
1. Clone the repository
2. Open the terminal
3. Navigate to the project
4. Add the firebase api keys and db url for the account created on firebase
5. Run the following commands to test the project

````````````````````````````````````````````````````````````
pip install -r requirements.txt
python3 test/test.py
````````````````````````````````````````````````````````````

PS. The Crypto module might not be found by pyrebase, since pycrypto is deprecated and pycryptodome has a different structure. In such a case, check if the Crypto module is present at site packages and rename if necessary.
