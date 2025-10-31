document.addEventListener('DOMContentLoaded', () => {
    if (typeof lucide !== 'undefined') lucide.createIcons();

    // ---------------- Elements ----------------
    const profileContainer = document.getElementById('profile-container');
    const editButton = document.getElementById('edit-profile-button');
    const saveButton = document.getElementById('save-profile-button');
    const cancelButton = document.getElementById('cancel-profile-button');
    const profileInput = document.getElementById('profile-picture-input');
    const profilePicture = document.getElementById('profile-picture');
    const editProfilePicButton = document.getElementById('edit-profile-pic-button');

    const uploadUrl = profileContainer?.dataset.uploadUrl;
    const updateProfileUrl = profileContainer?.dataset.updateProfileUrl;
    const csrfToken = profileContainer?.dataset.csrfToken;

    const defaultProfileUrl = "https://qimrryerxdzfewbkoqyq.supabase.co/storage/v1/object/public/ProfilePicture/avatar.png";

    // ---------------- Tabs ----------------
    const tabTriggers = document.querySelectorAll(".tab-trigger");
    const tabContents = document.querySelectorAll(".tab-content");
    tabTriggers.forEach(trigger => {
        trigger.addEventListener("click", () => {
            const target = trigger.dataset.tab;
            tabTriggers.forEach(t => t.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));
            trigger.classList.add("active");
            const targetEl = document.getElementById(target);
            if (targetEl) targetEl.classList.add("active");
        });
    });

    // ---------------- Edit Mode ----------------
    function toggleEditMode(enable) {
        profileContainer.classList.toggle('edit-mode', enable);
        profileContainer.classList.toggle('read-only', !enable);
        const actions = document.getElementById('profile-actions');
        if (actions) actions.style.display = enable ? 'flex' : 'none';
        if (editProfilePicButton) editProfilePicButton.style.display = enable ? 'block' : 'none';
    }

    editButton?.addEventListener('click', () => toggleEditMode(true));
    cancelButton?.addEventListener('click', () => {
        // Reset inputs
        document.querySelectorAll('.editable-field input, .editable-field textarea').forEach(input => {
            const displayEl = document.querySelector(`.field-value[data-field="${input.name}"]`);
            if (displayEl) input.value = displayEl.textContent;
        });
        toggleEditMode(false);
    });

    // ---------------- Update display instantly ----------------
    function updateDisplayField(fieldName, value) {
        const displayEl = document.querySelector(`.field-value[data-field="${fieldName}"]`);
        if (displayEl) displayEl.textContent = value;
    }
    document.querySelectorAll('.editable-field input, .editable-field textarea').forEach(input => {
        input.addEventListener('input', () => updateDisplayField(input.name, input.value));
    });

    // ---------------- Save profile ----------------
    saveButton?.addEventListener('click', async () => {
        if (!updateProfileUrl || !csrfToken) return;
        const formDataObj = {};
        document.querySelectorAll('#profile-container .editable-field input, #profile-container .editable-field textarea')
            .forEach(input => formDataObj[input.name] = input.value);

        try {
            const res = await fetch(updateProfileUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify(formDataObj)
            });
            const data = await res.json();

            if (data.status === 'success') {
                for (const key in formDataObj) updateDisplayField(key, formDataObj[key]);
                toggleEditMode(false);
                alert("Profile updated successfully!");
            } else {
                alert("Error updating profile: " + (data.message || "Unknown error"));
            }
        } catch (err) {
            console.error(err);
            alert("An error occurred while updating the profile.");
        }
    });

    // ---------------- Profile Picture ----------------
    function updateProfileImage(url) {
        // Update profile page
        if (profilePicture) {
            profilePicture.innerHTML = `<img src="${url}" alt="Profile Picture" class="rounded-full w-32 h-32 object-cover">`;
        }
        // Update sidebar
        updateSidebarProfilePicture(url);
        // Save to localStorage so it persists across pages
        localStorage.setItem("teacherProfileUrl", url);
    }

    function updateSidebarProfilePicture(url) {
        const avatarImg = document.querySelector('.teacher-avatar img.avatar-circle');
        const avatarDiv = document.querySelector('.teacher-avatar');
        if (avatarImg) avatarImg.src = url;
        else if (avatarDiv) avatarDiv.innerHTML = `<img src="${url}" alt="Profile Picture" class="avatar-circle">`;
    }

    editProfilePicButton?.addEventListener('click', () => profileInput.click());

    profileInput?.addEventListener('change', async () => {
        const file = profileInput.files[0];
        if (!file) return;

        // Preview locally
        const reader = new FileReader();
        reader.onload = e => updateProfileImage(e.target.result);
        reader.readAsDataURL(file);

        // Upload to server
        const uploadData = new FormData();
        uploadData.append('file', file);

        try {
            const res = await fetch(uploadUrl, { method: 'POST', headers: { 'X-CSRFToken': csrfToken }, body: uploadData });
            const data = await res.json();

            if (data.status === 'success') {
                updateProfileImage(data.url);
                alert('Profile picture updated successfully!');
            } else throw new Error(data.message || 'Upload failed');
        } catch (err) {
            console.error('Upload error:', err);
            alert('Failed to upload profile picture: ' + err.message);
        }
    });


     function ensureProfilePictureExists() {
    const profilePicDiv = document.getElementById('profile-picture');
    const currentImg = profilePicDiv.querySelector('img');

    if (!currentImg) {
        updateProfileImage(defaultProfileUrl);
        return;
    }

    const currentUrl = currentImg.src;
    if (!currentUrl || currentUrl.trim() === "") {
        updateProfileImage(defaultProfileUrl);
        return;
    }

    fetch(currentUrl, { method: 'HEAD' })
        .then(res => {
            if (!res.ok) updateProfileImage(defaultProfileUrl);
        })
        .catch(() => updateProfileImage(defaultProfileUrl));
}
    ensureProfilePictureExists();
});
