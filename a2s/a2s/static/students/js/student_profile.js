

lucide.createIcons();

// Tabs
document.querySelectorAll('.tab-trigger').forEach(trigger => {
    trigger.addEventListener('click', () => {
        const targetTab = trigger.getAttribute('data-tab');
        document.querySelectorAll('.tab-trigger').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        trigger.classList.add('active');
        document.getElementById(targetTab).classList.add('active');
    });
});
const cancelButton = document.getElementById('cancel-profile-button');
cancelButton.addEventListener('click', () => {
    profileContainer.classList.remove('edit-mode');
    profileContainer.classList.add('read-only');

    // hide buttons
    document.getElementById('profile-actions').style.display = 'none';

    // Reset form fields to original values
    document.querySelectorAll('.editable-field input, .editable-field textarea').forEach(input => {
        const fieldName = input.name;
        const displayEl = document.querySelector(`.field-value[data-field="${fieldName}"]`);
        if(displayEl) input.value = displayEl.textContent;
    });
});


// Edit Mode Toggle
const editButton = document.getElementById('edit-profile-button');
const profileContainer = document.getElementById('profile-container');
const saveButton = document.getElementById('save-profile-button');

editButton.addEventListener('click', () => {
    profileContainer.classList.toggle('edit-mode');
    profileContainer.classList.toggle('read-only');

    const inEditMode = profileContainer.classList.contains('edit-mode');
    const actions = document.getElementById('profile-actions');
    if(actions) actions.style.display = inEditMode ? 'flex' : 'none';
});

saveButton.addEventListener('click', () => {
    const formData = {};
    
    document.querySelectorAll('#profile-container .editable-field input, #profile-container .editable-field textarea')
        .forEach(input => {
            let value = input.value;
            if (['credits_completed','credits_required','academic_year'].includes(input.name)) value = parseInt(value) || 0;
            if (input.name === 'gpa') value = parseFloat(value) || 0;
            formData[input.name] = value;
        });

    fetch("{% url 'UpdateStudentProfile' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify(formData)
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            // Update profile card fields
            for(const key in formData){
                const display = document.querySelector(`.field-value[data-field="${key}"]`);
                if(display) display.textContent = formData[key];
                
            }
            // Update top profile card
            const fullNameEl = document.querySelector('[data-field="full_name"]');
            if(fullNameEl) fullNameEl.textContent = `${formData.first_name} ${formData.last_name}`;

            const badgeEl = document.querySelector('[data-field="year_major"]');
            if(badgeEl) badgeEl.textContent = `${formatYear(parseInt(formData.academic_year)||1)} • ${formData.major}`;



            // Update sidebar dynamically
            const sidebarName = document.getElementById('student-name');
            if(sidebarName) sidebarName.textContent = `${formData.first_name} ${formData.last_name}`;

            const sidebarProgram = document.getElementById('student-program');
            if(sidebarProgram) sidebarProgram.textContent = formData.major || formData.program;

            const sidebarYear = document.getElementById('student-year');
            if(sidebarYear) sidebarYear.textContent = getYearSuffix(parseInt(formData.academic_year) || 1);

            // Back to read-only mode
            profileContainer.classList.remove('edit-mode');
            profileContainer.classList.add('read-only');
            saveButton.style.display = 'none';

            alert("Profile updated successfully!");
        } else {
            alert("Error updating profile: " + (data.message || "Unknown error"));
        }
    })
    .catch(err => {
        console.error(err);
        alert("An error occurred while updating the profile.");
    });
});

// Academic Year formatter
function formatYear(year){
    if(year<=1) return "1st Year";
    if(year===2) return "2nd Year";
    if(year===3) return "3rd Year";
    if(year===4) return "4th Year";
    if(year>=5) return "5th Year";
    return year+"th Year";
}

// Instant update while typing
document.querySelectorAll('.editable-field input, .editable-field textarea').forEach(input=>{
    input.addEventListener('input', ()=>{
        const el = document.querySelector(`.field-value[data-field="${input.name}"]`);
        if(el) el.textContent = input.value;
    });
});
