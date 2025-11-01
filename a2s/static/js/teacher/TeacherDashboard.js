document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();

  // ================= TABS =================
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


  // ================= CALENDAR =================
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
const calendarJSON = window.calendarJSON || [];

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
    currentMonth = currentMonth === 0 ? 11 : currentMonth - 1;
    currentYear = currentMonth === 11 ? currentYear - 1 : currentYear;
    renderCalendar();
  });

  nextBtn.addEventListener("click", () => {
    currentMonth = currentMonth === 11 ? 0 : currentMonth + 1;
    currentYear = currentMonth === 0 ? currentYear + 1 : currentYear;
    renderCalendar();
  });

  calendarYearSelect.addEventListener("change", renderCalendar);
  calendarSemesterSelect.addEventListener("change", renderCalendar);
  renderCalendar();

  // Modal close
  const modal = document.getElementById("eventModal");
  const closeModal = modal.querySelector(".close");
  closeModal.onclick = () => (modal.style.display = "none");
  window.onclick = e => {
    if (e.target === modal) modal.style.display = "none";
  };
});
