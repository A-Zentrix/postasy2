# Delete Button Troubleshooting Guide

## Current Status
The delete button functionality has been simplified and enhanced with debugging features to identify and resolve any issues.

## Debugging Features Added

### 1. **Console Logging**
- Function calls are logged to console
- User actions (confirm/cancel) are logged
- Form submission is logged
- Error details are logged

### 2. **Alert Messages**
- Shows when delete function is called
- Shows user confirmation status
- Shows form submission status

### 3. **Backend Debugging**
- Route calls are logged to server console
- Permission checks are logged
- File deletion status is logged
- Database operations are logged

## Testing Steps

### Step 1: Test Function Call
1. Open browser developer console (F12)
2. Click any delete button
3. Check for alert message: "Delete function called for poster: X - Y"
4. Check console for log: "Delete function called for poster: X, Y"

### Step 2: Test User Confirmation
1. Click "OK" in the confirmation dialog
2. Check for alert: "User confirmed deletion, submitting form..."
3. Check console for log: "User confirmed deletion"

### Step 3: Test Form Submission
1. Check console for log: "Submitting delete form for poster: X"
2. Check server console for logs:
   - "Delete route called for poster_id: X"
   - "Current user: Y"
   - "Poster found: Z, user_id: Y"

### Step 4: Test Backend Processing
1. Check server console for permission logs
2. Check for file deletion logs
3. Check for database deletion logs
4. Check for success message

## Common Issues and Solutions

### Issue 1: Function Not Called
**Symptoms**: No alert appears when clicking delete button
**Possible Causes**:
- JavaScript error preventing function execution
- Button onclick attribute not properly set
- Event handler not attached

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify button HTML has correct onclick attribute
3. Test with the "Test Delete" button

### Issue 2: Confirmation Dialog Not Appearing
**Symptoms**: Alert appears but no confirmation dialog
**Possible Causes**:
- Browser blocking popups
- JavaScript confirm() function disabled

**Solutions**:
1. Allow popups for the site
2. Check browser security settings
3. Try in different browser

### Issue 3: Form Not Submitting
**Symptoms**: Confirmation works but no server logs
**Possible Causes**:
- Form action URL incorrect
- CSRF token issues
- Network connectivity problems

**Solutions**:
1. Check form action URL in browser network tab
2. Verify route exists and is accessible
3. Check server logs for any errors

### Issue 4: Permission Denied
**Symptoms**: Server logs show "Permission denied"
**Possible Causes**:
- User not logged in
- Poster belongs to different user
- Session expired

**Solutions**:
1. Verify user is logged in
2. Check poster ownership
3. Refresh page and try again

### Issue 5: File Not Found
**Symptoms**: Server logs show "File not found"
**Possible Causes**:
- Poster file was already deleted
- File path is incorrect
- File permissions issue

**Solutions**:
1. Check if poster file exists in uploads folder
2. Verify file path construction
3. Check file permissions

## Current Implementation

### Frontend (Simplified)
```javascript
function deletePoster(posterId, posterTitle) {
    console.log('Delete function called for poster:', posterId, posterTitle);
    alert(`Delete function called for poster: ${posterId} - ${posterTitle}`);
    
    if (confirm(`Are you sure you want to delete "${posterTitle}"? This action cannot be undone.`)) {
        console.log('User confirmed deletion');
        alert('User confirmed deletion, submitting form...');
        
        // Simple form submission approach
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/poster/${posterId}/delete`;
        
        document.body.appendChild(form);
        console.log('Submitting delete form for poster:', posterId);
        form.submit();
    } else {
        console.log('User cancelled deletion');
        alert('User cancelled deletion');
    }
}
```

### Backend (Enhanced Debugging)
```python
@poster_bp.route('/<int:poster_id>/delete', methods=['POST'])
@login_required
def delete(poster_id):
    print(f"Delete route called for poster_id: {poster_id}")
    print(f"Current user: {current_user.id}")
    
    poster = Poster.query.get_or_404(poster_id)
    print(f"Poster found: {poster.title}, user_id: {poster.user_id}")
    
    # Check permissions
    if poster.user_id != current_user.id:
        print(f"Permission denied: poster.user_id={poster.user_id}, current_user.id={current_user.id}")
        flash('You do not have permission to delete this poster.', 'danger')
        return redirect(url_for('poster.gallery'))
    
    print("Permission check passed, proceeding with deletion")
    
    # Delete file and database record with error handling
    # ... (implementation with detailed logging)
```

## Test Button
A "Test Delete" button has been added to the gallery page to help verify the delete function is working:
- Click the "Test Delete" button
- Check for alert messages
- Verify console logs
- Test the confirmation dialog

## Expected Behavior

### Successful Delete Flow:
1. **Click Delete Button** → Alert: "Delete function called for poster: X - Y"
2. **Confirm Deletion** → Alert: "User confirmed deletion, submitting form..."
3. **Form Submission** → Console: "Submitting delete form for poster: X"
4. **Server Processing** → Server logs show deletion process
5. **Success** → Page reloads, poster removed from gallery

### Error Flow:
1. **Permission Error** → Server logs show permission denied
2. **File Error** → Server logs show file not found
3. **Database Error** → Server logs show database error
4. **User Feedback** → Flash message shows error details

## Next Steps

1. **Test the current implementation** using the debugging features
2. **Check browser console** for any JavaScript errors
3. **Check server logs** for backend processing details
4. **Verify user permissions** and poster ownership
5. **Test with different browsers** to ensure compatibility

## Removal of Debug Features

Once the delete functionality is confirmed working:
1. Remove alert messages from deletePoster function
2. Remove print statements from backend route
3. Remove test button from gallery page
4. Keep console.log statements for future debugging

The current implementation provides comprehensive debugging to identify exactly where any issues occur in the delete process. 