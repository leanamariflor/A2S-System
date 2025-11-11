document.addEventListener("DOMContentLoaded", () => {
   lucide.createIcons();

  const defaultProfileUrl = "https://qimrryerxdzfewbkoqyq.supabase.co/storage/v1/object/public/ProfilePicture/avatar.png";

  // ===== Profile Avatar =====
  const avatarImg = document.querySelector(".student-avatar img.avatar-circle");
  const avatarDiv = document.querySelector(".student-avatar");

  if (!avatarImg && avatarDiv) {
    const storedUrl = localStorage.getItem("studentProfileUrl_");
    if (storedUrl)
       avatarDiv.innerHTML = `<img src="${storedUrl}" alt="Profile Picture" class="avatar-circle">`;
  }

  if (avatarImg) {
    avatarImg.onerror = () => {
      avatarImg.src = defaultProfileUrl
    };
    if (!avatarImg.src || avatarImg.src.trim() === "") 
      avatarImg.src = defaultProfileUrl;
  }

  window.updateSidebarProfilePicture = function (newUrl) {
    const avatarImg = document.querySelector(".student-avatar img.avatar-circle");
    const avatarSpan = document.querySelector(".student-avatar span");

    if (avatarImg)
       avatarImg.src = newUrl;
    else if (avatarSpan) {
      const avatarDiv = document.querySelector(".student-avatar");
      avatarDiv.innerHTML = `<img src="${newUrl}" alt="Profile Picture" class="avatar-circle">`;
    }
    localStorage.setItem("studentProfileUrl_" + USER_ID, newUrl);
  };

  // ===== Notifications =====
  const notifBtn = document.getElementById("notif-btn");
  const notifDropdown = document.getElementById("notif-dropdown");
  const notifList = document.getElementById("notif-list");
  const clearNotifBtn = document.getElementById("clear-notif");
  const notifCount = document.getElementById("notif-badge");

  if (notifBtn && notifDropdown) {
    const today = new Date();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay());
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 6);

    let readEvents = JSON.parse(localStorage.getItem("readNotifications_" + USER_ID) || "[]");

    // Store calendar data if exists
    if (typeof calendarJSON !== "undefined" && Array.isArray(calendarJSON)) {
      localStorage.setItem("studentCalendarData_" + USER_ID, JSON.stringify(calendarJSON));
    }

    const storedCalendar = JSON.parse(localStorage.getItem("studentCalendarData_" + USER_ID) || "[]");
    const allEvents = [];
    if (Array.isArray(storedCalendar)) {
      storedCalendar.forEach(sem => {
        if (sem.events && Array.isArray(sem.events)) {
          sem.events.forEach(ev => allEvents.push({
            id: ev.name + ev.date,
            date: new Date(ev.date),
            name: ev.name,
            type: ev.type,
            semester: sem.semester
          }));
        }
      });
    }

    let weekEvents = allEvents.filter(ev =>
      ev.date >= startOfWeek && ev.date <= endOfWeek && !readEvents.includes(ev.id)
    );

    function updateBadge() {
      if (notifCount) {
        if (weekEvents.length > 0) {
          notifCount.textContent = weekEvents.length;
          notifCount.classList.remove("hidden");
        } else notifCount.classList.add("hidden");
      }
    }

    function renderNotifications() {
      notifList.innerHTML =
        weekEvents.length > 0
          ? weekEvents.map(ev => `
            <div class="task-item" data-id="${ev.id}">
              <div class="task-details">
                <div class="task-title">${ev.name}</div>
                <div class="task-due">Date: ${ev.date.toLocaleDateString()}</div>
              </div>
              <div class="task-type">${ev.type}</div>
            </div>
          `).join("")
          : `<p>No events this week.</p>`;

      notifList.querySelectorAll(".task-item").forEach(item => {
        item.addEventListener("click", () => {
          const id = item.dataset.id;
          readEvents.push(id);
          localStorage.setItem("readNotifications_" + USER_ID, JSON.stringify(readEvents));
          item.remove();
          weekEvents = weekEvents.filter(ev => ev.id !== id);
          updateBadge();
        });
      });
    }

    clearNotifBtn.addEventListener("click", () => {
      weekEvents.forEach(ev => readEvents.push(ev.id));
      localStorage.setItem("readNotifications_" + USER_ID, JSON.stringify(readEvents));
      weekEvents = [];
      renderNotifications();
      updateBadge();
    });

    notifBtn.addEventListener("click", e => {
      e.stopPropagation();
      notifDropdown.style.display = notifDropdown.style.display === "block" ? "none" : "block";
    });

    document.addEventListener("click", e => {
      if (!notifDropdown.contains(e.target) && !notifBtn.contains(e.target)) {
        notifDropdown.style.display = "none";
      }
    });

    renderNotifications();
    updateBadge();
  }
});
