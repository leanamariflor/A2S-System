document.addEventListener("DOMContentLoaded", function() {
    const container = document.getElementById("advisor-notes-container");
    const editBtn = document.getElementById("editAdvisorNoteBtn");
    const saveBtn = document.getElementById("saveAdvisorNoteBtn");
    const noteDisplay = document.getElementById("advisorNoteText");
    const noteEdit = document.getElementById("advisorNoteEdit");

    const updateUrl = container.dataset.updateUrl;
    const csrfToken = container.dataset.csrfToken;

    // Edit button click
    editBtn.addEventListener("click", function() {
        noteEdit.value = noteDisplay.textContent.trim() === "No notes for this student yet."
            ? ""
            : noteDisplay.textContent.trim();

        noteDisplay.style.display = "none";
        noteEdit.style.display = "block";
        editBtn.style.display = "none";
        saveBtn.style.display = "inline-block";
    });

    // Save button click
    saveBtn.addEventListener("click", function() {
        const updatedNote = noteEdit.value.trim();

        fetch(updateUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ student_notes: updatedNote })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                // Update display
                noteDisplay.textContent = data.notes || "No notes for this student yet.";

                // Update table notes
                document.querySelectorAll(".note-text").forEach(td => {
                    td.textContent = data.notes || "No notes yet";
                });

                // Switch back to view mode
                noteDisplay.style.display = "block";
                noteEdit.style.display = "none";
                editBtn.style.display = "inline-block";
                saveBtn.style.display = "none";
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch(err => alert("Error: " + err));
    });
});
