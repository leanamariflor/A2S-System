document.addEventListener("DOMContentLoaded", () => {
  if (typeof lucide !== "undefined") lucide.createIcons();

  const defaultProfileUrl = "https://qimrryerxdzfewbkoqyq.supabase.co/storage/v1/object/public/ProfilePicture/avatar.png";

  // ===== Profile Avatar (unchanged) =====
  const avatarImg = document.querySelector(".student-avatar img.avatar-circle");
  const avatarDiv = document.querySelector(".student-avatar");

  if (!avatarImg && avatarDiv) {
    const storedUrl = localStorage.getItem("studentProfileUrl");
    if (storedUrl) avatarDiv.innerHTML = `<img src="${storedUrl}" alt="Profile Picture" class="avatar-circle">`;
  }

  if (avatarImg) {
    avatarImg.onerror = () => (avatarImg.src = defaultProfileUrl);
    if (!avatarImg.src || avatarImg.src.trim() === "") avatarImg.src = defaultProfileUrl;
  }

  window.updateSidebarProfilePicture = function (newUrl) {
    const avatarImg = document.querySelector(".student-avatar img.avatar-circle");
    const avatarSpan = document.querySelector(".student-avatar span");

    if (avatarImg) avatarImg.src = newUrl;
    else if (avatarSpan) {
      const avatarDiv = document.querySelector(".student-avatar");
      avatarDiv.innerHTML = `<img src="${newUrl}" alt="Profile Picture" class="avatar-circle">`;
    }

    localStorage.setItem("studentProfileUrl", newUrl);
  };

  // ===== Notifications =====
  const notifBtn = document.getElementById("notif-btn");
  const notifDropdown = document.getElementById("notif-dropdown");
  const notifList = document.getElementById("notif-list");
  const clearNotifBtn = document.getElementById("clear-notif");
  const notifCount = document.getElementById("notif-badge");

  const today = new Date();
  const startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - today.getDay());
  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(startOfWeek.getDate() + 6);

  // flatten all events from JSON
  const allEvents = [];
  if (typeof calendarJSON !== "undefined" && Array.isArray(calendarJSON)) {
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
  }

  // get read notifications from localStorage
  const readEvents = JSON.parse(localStorage.getItem("readNotifications") || "[]");

  // only include unread events
  const weekEvents = allEvents.filter(ev => {
    return ev.date >= startOfWeek && ev.date <= endOfWeek && !readEvents.includes(ev.name + ev.date.toISOString());
  });

  let unreadCount = weekEvents.length;

  function renderNotifications() {
    const notifHTML = weekEvents.length
      ? weekEvents.map(ev => `
          <div class="task-item" data-id="${ev.name + ev.date.toISOString()}">
            <div class="task-details">
              <div class="task-title">
                ${ev.name}
                ${Math.abs((ev.date - today) / (1000 * 60 * 60 * 24)) <= 2 ? '<span class="urgent"></span>' : ''}
              </div>
              <div class="task-due">Date: ${ev.date.toLocaleDateString()}</div>
            </div>
            <div class="task-type">${ev.type}</div>
          </div>
        `).join("")
      : `<p>No events this week.</p>`;

    if (notifList) notifList.innerHTML = notifHTML;

    // mark as read
    const taskItems = notifList.querySelectorAll(".task-item");
    taskItems.forEach(item => {
      item.addEventListener("click", () => {
        const id = item.dataset.id;
        readEvents.push(id);
        localStorage.setItem("readNotifications", JSON.stringify(readEvents));
        item.remove();
        unreadCount = weekEvents.length - readEvents.length;
        updateBadge();
      });
    });
  }

  renderNotifications();

  function updateBadge() {
    if (notifCount) {
      if (unreadCount > 0) {
        notifCount.textContent = unreadCount;
        notifCount.classList.remove("hidden");
      } else {
        notifCount.classList.add("hidden");
      }
    }
  }

  updateBadge();

  if (notifBtn && notifDropdown) {
    notifBtn.addEventListener("click", e => {
      e.stopPropagation();
      const isVisible = notifDropdown.style.display === "block";
      notifDropdown.style.display = isVisible ? "none" : "block";
      if (!isVisible) {
        unreadCount = weekEvents.length - readEvents.length;
        updateBadge();
      }
    });

    document.addEventListener("click", e => {
      if (!notifDropdown.contains(e.target) && !notifBtn.contains(e.target)) {
        notifDropdown.style.display = "none";
      }
    });
  }

  if (clearNotifBtn) {
    clearNotifBtn.addEventListener("click", () => {
      weekEvents.forEach(ev => readEvents.push(ev.name + ev.date.toISOString()));
      localStorage.setItem("readNotifications", JSON.stringify(readEvents));
      unreadCount = 0;
      renderNotifications();
      updateBadge();
    });
  }
});
