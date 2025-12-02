document.addEventListener('DOMContentLoaded', () => {
   lucide.createIcons();
  const sectionSelect = document.getElementById('sectionSelect');
  const viewSectionBtn = document.getElementById('viewSectionBtn');
  const showAllBtn = document.getElementById('showAllBtn');
  const courseTable = document.getElementById('courseTable');
  const rows = courseTable.querySelectorAll('.course-row');

  viewSectionBtn.addEventListener('click', () => {
    const selectedValue = sectionSelect.value;
    if (!selectedValue) {
      alert('Please select a course/section first.');
      return;
    }

    const [selectedCourse, selectedSection] = selectedValue.split('|');

    rows.forEach(row => {
      const courseCode = row.querySelector('td:nth-child(1)').innerText.trim();
      const section = row.querySelector('td:nth-child(2)').innerText.trim();

      if (courseCode === selectedCourse && section === selectedSection) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  });

  showAllBtn.addEventListener('click', () => {
    rows.forEach(row => {
      row.style.display = '';
    });
    sectionSelect.value = '';
  });
});
