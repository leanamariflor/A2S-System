document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();

  // Tabs
  document.querySelectorAll(".tab-trigger").forEach(trigger => {
    trigger.addEventListener("click", () => {
      const target = trigger.dataset.tab;
      document.querySelectorAll(".tab-trigger").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      trigger.classList.add("active");
      document.getElementById(target).classList.add("active");
    });
  });

  // Edit mode logic
  const editButton = document.getElementById("edit-profile-button");
  const profileContainer = document.getElementById("profile-container");
  const profileActions = document.getElementById("profile-actions");
  const saveButton = document.getElementById("save-profile-button");
  const cancelButton = document.getElementById("cancel-profile-button");

  function toggleEditMode(enable) {
    if (enable) {
      profileContainer.classList.add("edit-mode");
      profileContainer.classList.remove("read-only");
      profileActions.style.display = "flex";
    } else {
      profileContainer.classList.remove("edit-mode");
      profileContainer.classList.add("read-only");
      profileActions.style.display = "none";
    }
  }

  editButton.addEventListener("click", () => {
    const isEditing = profileContainer.classList.contains("edit-mode");
    toggleEditMode(!isEditing);
  });

  // Cancel changes
  cancelButton.addEventListener("click", () => {
    toggleEditMode(false);
    document.querySelectorAll(".editable-field input, .editable-field textarea, .editable-field select").forEach(input => {
      const displayEl = document.querySelector(`.field-value[data-field="${input.name}"]`);
      if (displayEl) input.value = displayEl.textContent.trim();
    });
  });

  // Save changes
  saveButton.addEventListener("click", () => {
    const formData = {};
    document.querySelectorAll("#profile-container .editable-field input, #profile-container .editable-field textarea, #profile-container .editable-field select").forEach(input => {
      formData[input.name] = input.value;
    });

    fetch(window.teacherProfileConfig.updateUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": window.teacherProfileConfig.csrfToken
      },
      body: JSON.stringify(formData)
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          for (const key in formData) {
            const display = document.querySelector(`.field-value[data-field="${key}"]`);
            if (display) display.textContent = formData[key];
          }
          const fullNameEl = document.querySelector("[data-field='full_name']");
          if (fullNameEl) fullNameEl.textContent = `${formData.first_name} ${formData.last_name}`;
          toggleEditMode(false);
          alert("Profile updated successfully!");
        } else alert("Error: " + (data.message || "Unknown"));
      })
      .catch(err => {
        console.error(err);
        alert("An error occurred while updating the profile.");
      });
  });

  // Live preview while typing
  document.querySelectorAll(".editable-field input, .editable-field textarea, .editable-field select").forEach(input => {
    input.addEventListener("input", () => {
      const el = document.querySelector(`.field-value[data-field='${input.name}']`);
      if (el) el.textContent = input.value;
    });
  });
});
