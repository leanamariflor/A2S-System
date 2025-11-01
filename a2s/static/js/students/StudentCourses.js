document.addEventListener("DOMContentLoaded", () => {
  const courseList = document.querySelector("#coursesList");
  const buttons = document.querySelectorAll(".tab-btn");
  let allCourses = [];

  const studentProgram = STUDENT_PROGRAM || "";
  if (!studentProgram) {
    courseList.innerHTML = `<p style="color:red;">No program assigned to your profile.</p>`;
    return;
  }

  const semStart = SEMESTER_START || "";
  const semEnd = SEMESTER_END || "";

  fetch(`/students/api/curriculum/${studentProgram}/`)
    .then(response => {
      if (!response.ok) throw new Error("No curriculum found for " + studentProgram);
      return response.json();
    })
    .then(data => {
      const curriculum = data.curriculum || [];

      curriculum.forEach(year => {
        (year.terms || []).forEach(term => {
          (term.subjects || []).forEach(sub => {
            let percent = 0;

           
            if (sub.final_grade === "PASSED" || (typeof sub.final_grade === "number" && sub.final_grade <= 3.0)) {
              percent = 100;
            } else if (sub.final_grade === "CURRENT") {
              percent = calculateOngoingProgress();
            } else if (sub.final_grade === "RECOMMENDED") {
              percent = 0;
            } else if (sub.final_grade && !isNaN(sub.final_grade)) {
              percent = Math.min(parseFloat(sub.final_grade) / 5 * 100, 99);
            }

            allCourses.push({
              code: sub.subject_code,
              name: sub.description,
              units: sub.units,
              grade: sub.final_grade,
              progress: percent
            });
          });
        });
      });

      showCourses("current");
    })
    .catch(err => {
      console.error("Error loading curriculum:", err);
      courseList.innerHTML = `<p style="color:red;">Error loading your courses: ${err.message}</p>`;
    });

  function calculateOngoingProgress() {
    if (!semStart || !semEnd) return 50;
    const now = new Date();
    const start = new Date(semStart);
    const end = new Date(semEnd);
    const total = end - start;
    const elapsed = now - start;
    return Math.max(0, Math.min(100, (elapsed / total) * 100));
  }

  function showCourses(type) {
    courseList.innerHTML = "";
    let filtered = [];

    if (type === "current") {
      filtered = allCourses.filter(c =>
        ["CURRENT", "ONGOING", null, "", undefined].includes(c.grade)
      );
    } else if (type === "completed") {
      filtered = allCourses.filter(c =>
        c.grade === "PASSED" ||
        (typeof c.grade === "number" && c.grade <= 3.0) ||
        (!isNaN(parseFloat(c.grade)) && parseFloat(c.grade) <= 3.0)
      );
    } else if (type === "recommended") {
      filtered = allCourses.filter(c =>
        ["RECOMMENDED", "TO_TAKE", "FUTURE"].includes(c.grade)
      );
    }

    if (filtered.length === 0) {
      courseList.innerHTML = `<p class="empty-msg">No ${type} courses found.</p>`;
      return;
    }

    filtered.forEach(c => {
      const div = document.createElement("div");
      div.classList.add("course-item");
      div.innerHTML = `
        <div class="course-info">
          <h4>${c.code} - ${c.name}</h4>
          <p>${c.units} Units</p>
        </div>
        <div class="course-progress">
          <div class="progress-bar">
            <div class="progress-fill ${c.progress === 100 ? 'completed' : ''}" style="width:${c.progress}%"></div>
          </div>
          <span>${Math.round(c.progress)}%</span>
        </div>
      `;
      courseList.appendChild(div);
    });
  }

  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      buttons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      showCourses(btn.dataset.target);
    });
  });
});
