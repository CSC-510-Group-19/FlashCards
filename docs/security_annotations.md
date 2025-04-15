#Security Annotations
Endpoints are now secured by optional annotations checking against various security rules.  Use of the annotation requires adding the user's idToken to the request Authorization header.
If any annotation detects an error, they will return an http error to the client, preventing the controller function from being ran.

##@token_required
@token_required validates that the rest call includes a header with a valid authorization token. Will return error messages corresponding to the problem detected.

##@has_folder_rights
@has_folder_rights validates that user is a valid user via authorization token and that the user is the owner of the folder corresponding to param folder_id.

##@has_deck_rights
@has_deck_rights validates that user is a valid user via authorization token and that the user is the owner of the deck corresponding to param deck_id.

##@deck_is_visible
@deck_is_visible validates that the user is a valid user via authorization token and that the user is allowed to see a deck corresponding to param deck_id.
This cheeck is done by checking if user is the owner of the deck or if the deck's visibility is set to public.

##@has_folder_and_deck_rights
@has_folder_and_deck_rights validates that the user has permission to modify both the folder and deck corresponding to the POST body attributes folderId and deckId.
