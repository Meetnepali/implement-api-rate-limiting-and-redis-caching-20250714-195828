# Guidance for Task: User Profile Avatar Management API

This project is a FastAPI-based user profile avatar management service. It contains foundation code for avatar upload and retrieval endpoints, focusing on secure file handling, user association, validation, and modern API practices.

## What You Need to Do

You must *implement* or *complete* two endpoints using FastAPI:

1. **POST /users/me/avatar**  
   Allow authenticated users to upload an avatar image (PNG or JPEG, up to 2MB):
   - Accepts multipart/form-data with a single image file field.
   - Enforces MIME type, file size, and proper file extension.
   - Avoid filename collisions and store avatars associated with each user.
   - Removes previous avatar file if present.
   - Responds with a structured payload including avatar URL and user ID.
   - Logs all upload attempts, including failures with reasons.
   - Includes robust validation and error reporting for invalid uploads (wrong type, too big, etc).
   - Requires authentication (see below).

2. **GET /users/{user_id}/avatar**
   - Serves avatar file for any user by user ID, with correct content type and headers for image display or download.
   - Handles missing user, missing file, or user without avatar gracefully (proper 404/error responses).

### Additional Requirements
- Use Pydantic response models for API results and errors.
- Employ FastAPI dependency injection for simulated authentication and user lookup.
- Perform async file IO for upload.
- Add structured logging (success/failure, user id, reason when applicable).
- Ensure endpoints are correctly described in OpenAPI docs: parameter docs, error schema, response examples, auth info.
- Code structure should be clean and maintainable.

## Authentication Notes
- *For this exercise*, authentication is simulated: sending the user id in the `Authorization: Bearer ...` header suffices (see `get_current_user` for details).

## Example Flows
- User uploads their avatar (valid file): endpoint returns 201 and URL.
- User uploads wrong file type or too large: 400/413 error response, with detail message.
- Request avatar for user with no avatar: returns 404 error with explanation.

## Verifying Your Solution
- Confirm avatar upload rejects wrong types and too-large files.
- Confirm logging occurs for upload attempts (success and failure).
- Ensure uploaded file replaces any previous avatar for the same user.
- Check GET returns correct image (with correct headers) when avatar is present, and appropriate 404 when not.
- Review FastAPI docs (`/docs`) for endpoint documentation, parameters, security, example responses and error docs.
- Validate error handling covers all edge cases per requirements.

**Reminder:** Do not include setup, build, or run instructions in your response.
