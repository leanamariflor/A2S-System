document.addEventListener("DOMContentLoaded", () => {
  if (typeof lucide !== "undefined") lucide.createIcons();

  // =================== TAB NAVIGATION ===================
  const tabTriggers = document.querySelectorAll(".tab-trigger");
  const tabContents = document.querySelectorAll(".tab-content");
  tabTriggers.forEach(trigger => {
    trigger.addEventListener("click", () => {
      const target = trigger.dataset.tab;
      tabTriggers.forEach(t => t.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));
      trigger.classList.add("active");
      document.getElementById(target).classList.add("active");
    });
  });

  // =================== CURRICULUM ===================
  const container = document.getElementById("curriculum-container");
  const yearSelect = document.getElementById("yearSelect");
  const filterButtons = document.querySelectorAll(".filter-btn");

  let allData = Array.isArray(curriculumJSON) ? curriculumJSON : [];
  let activeFilter = "All";
  let activeYear = "All";

  function renderCurriculum(data) {
  container.innerHTML = "";

  if (!data.length) {
    container.innerHTML = "<p>No curriculum data available for this program.</p>";
    return;
  }

  let hasAnyMatch = false;

  data.forEach(year => {
    const yearBlock = document.createElement("div");
    yearBlock.classList.add("year-block");

    if (activeYear !== "All" && year.year !== activeYear) return;

    const filteredTerms = year.terms.map(term => {
      const matchedSubjects = term.subjects.filter(subj => {
        if (activeFilter === "All") return true;
        if (activeFilter === "PASSED") return subj.final_grade === "PASSED";
        if (activeFilter === "CURRENT") return subj.final_grade === "CURRENT";
        if (activeFilter === "RECOMMENDED") return subj.final_grade === "RECOMMENDED";
        return false;
      });
      return { ...term, subjects: matchedSubjects };
    }).filter(term => term.subjects.length > 0);

    if (!filteredTerms.length) return;

    hasAnyMatch = true;
    yearBlock.innerHTML = `<h3>${year.year}</h3>`;

    filteredTerms.forEach(term => {
      const table = document.createElement("table");
      const header = `
        <thead>
          <tr>
            <th>Term</th><th>Subject Code</th><th>Description</th>
            <th>Units</th><th>School Year</th><th>Semester</th><th>Status</th>
          </tr>
        </thead>`;
      const rows = term.subjects.map(subj => `
        <tr>
          <td>${term.term}</td>
          <td>${subj.subject_code}</td>
          <td>${subj.description}</td>
          <td>${subj.units}</td>
          <td>${subj.school_year}</td>
          <td>${subj.semester}</td>
          <td>${subj.final_grade}</td>
        </tr>`).join("");

      table.innerHTML = header + `<tbody>${rows}</tbody>`;
      yearBlock.appendChild(table);
    });

    container.appendChild(yearBlock);
  });

  if (!hasAnyMatch) {
    container.innerHTML = `<p>No ${activeFilter.toLowerCase()} subjects found for the selected year.</p>`;
  }
}


  if (studentProgram && studentProgram !== "Undeclared") {
    renderCurriculum(allData);
  } else {
    container.innerHTML = `<p style="color:red;">Program not set for this student.</p>`;
  }

  filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      filterButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeFilter = btn.dataset.filter;
      renderCurriculum(allData);
    });
  });

  yearSelect.addEventListener("change", e => {
    activeYear = e.target.value;
    renderCurriculum(allData);
  });

  // =================== CALENDAR ===================
  const calendarGrid = document.getElementById("calendar-grid");
  const monthTitle = document.getElementById("month-title");
  const prevBtn = document.getElementById("prev-month");
  const nextBtn = document.getElementById("next-month");
  const calendarYearSelect = document.getElementById("calendarYearSelect");
  const calendarSemesterSelect = document.getElementById("calendarSemesterSelect");

  let currentDate = new Date();
  let currentYear = currentDate.getFullYear();
  let currentMonth = currentDate.getMonth();
  const months = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
  ];

  const eventColors = {
    "Holiday": "#ffcccc",
    "Class Start": "#cce5ff",
    "Class End": "#d4edda",
    "Exam": "#fff3cd",
    "Deadline": "#f8d7da",
    "Ceremony": "#e2e3e5",
    "Special Non-Working Day": "#f0b3ff"
  };

  const allEvents = [];
  calendarJSON.forEach(sem => {
    sem.events.forEach(ev => {
      allEvents.push({
        date: new Date(ev.date),
        name: ev.name,
        type: ev.type,
        semester: sem.semester
      });
    });
  });

  const years = [...new Set(allEvents.map(e => e.date.getFullYear()))];
  const semesters = [...new Set(allEvents.map(e => e.semester))];
  calendarYearSelect.innerHTML = `<option value="All">All</option>` + years.map(y => `<option>${y}</option>`).join("");
  calendarSemesterSelect.innerHTML = `<option value="All">All</option>` + semesters.map(s => `<option>${s}</option>`).join("");

  function renderCalendar() {
    const selectedYear = calendarYearSelect.value;
    const selectedSem = calendarSemesterSelect.value;
    calendarGrid.innerHTML = "";
    monthTitle.textContent = `${months[currentMonth]} ${currentYear}`;

    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const lastDate = new Date(currentYear, currentMonth + 1, 0).getDate();

    const header = document.createElement("div");
    header.className = "calendar-row header";
    ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].forEach(day => {
      const cell = document.createElement("div");
      cell.className = "calendar-cell header";
      cell.textContent = day;
      header.appendChild(cell);
    });
    calendarGrid.appendChild(header);

    let row = document.createElement("div");
    row.className = "calendar-row";

    for (let i = 0; i < firstDay; i++) {
      const empty = document.createElement("div");
      empty.className = "calendar-cell empty";
      row.appendChild(empty);
    }

    for (let d = 1; d <= lastDate; d++) {
      const cell = document.createElement("div");
      cell.className = "calendar-cell";
      cell.innerHTML = `<span class="date-number">${d}</span>`;
      const today = new Date();
      if (d === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear()) {
        cell.classList.add("today");
      }

      allEvents.forEach(ev => {
        if (
          ev.date.getFullYear() === currentYear &&
          ev.date.getMonth() === currentMonth &&
          ev.date.getDate() === d &&
          (selectedYear === "All" || ev.date.getFullYear() == selectedYear) &&
          (selectedSem === "All" || ev.semester === selectedSem)
        ) {
          const badge = document.createElement("span");
          badge.className = "event-badge";
          badge.style.backgroundColor = eventColors[ev.type] || "#eee";
          badge.textContent = ev.name.length > 12 ? ev.name.substring(0, 12) + "..." : ev.name;
          badge.addEventListener("click", () => {
            document.getElementById("eventName").textContent = ev.name;
            document.getElementById("eventType").textContent = ev.type;
            document.getElementById("eventDate").textContent = ev.date.toDateString();
            document.getElementById("eventModal").style.display = "flex";
          });
          cell.appendChild(badge);
        }
      });

      row.appendChild(cell);
      if ((d + firstDay) % 7 === 0 || d === lastDate) {
        calendarGrid.appendChild(row);
        row = document.createElement("div");
        row.className = "calendar-row";
      }
    }
  }

  prevBtn.addEventListener("click", () => {
    if (currentMonth === 0) { currentMonth = 11; currentYear--; } 
    else currentMonth--;
    renderCalendar();
  });

  nextBtn.addEventListener("click", () => {
    if (currentMonth === 11) { currentMonth = 0; currentYear++; } 
    else currentMonth++;
    renderCalendar();
  });

  calendarYearSelect.addEventListener("change", (e) => {
  const selectedYear = e.target.value;

  if (selectedYear !== "All") {
    const yearEvents = allEvents.filter(ev => ev.date.getFullYear() == selectedYear);
    if (yearEvents.length > 0) {
      currentYear = parseInt(selectedYear);
      currentMonth = yearEvents[0].date.getMonth(); 
    } else {
      currentYear = parseInt(selectedYear);
      currentMonth = 0;
    }
  }

  renderCalendar();
});

  calendarSemesterSelect.addEventListener("change", renderCalendar);
  renderCalendar();

  // =================== MODAL ===================
  const modal = document.getElementById("eventModal");
  const closeModal = modal.querySelector(".close");
  closeModal.onclick = () => (modal.style.display = "none");
  window.onclick = e => { if (e.target === modal) modal.style.display = "none"; };

  // =================== NOTIFICATIONS ===================
  const notificationsContainer = document.getElementById("recentNotificationsContainer");
  const today = new Date();
  const startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - today.getDay());
  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(startOfWeek.getDate() + 6);

  const weekEvents = allEvents.filter(ev => ev.date >= startOfWeek && ev.date <= endOfWeek);

  if (weekEvents.length > 0) {
    notificationsContainer.innerHTML = weekEvents.map(ev => `
      <div class="task-item">
        <div class="task-details">
          <div class="task-title">
            ${ev.name}
            ${Math.abs((ev.date - today) / (1000 * 60 * 60 * 24)) <= 2 ? '<span class="urgent"></span>' : ''}
          </div>
          <div class="task-due">Date: ${ev.date.toLocaleDateString()}</div>
        </div>
        <div class="task-type">${ev.type}</div>
      </div>
    `).join("");
  } else {
    notificationsContainer.innerHTML = `<p>No events this week.</p>`;
  }
});
