document.addEventListener("DOMContentLoaded", () => {
  const defaultProfileUrl =
    "https://qimrryerxdzfewbkoqyq.supabase.co/storage/v1/object/public/ProfilePicture/avatar.png";

  const avatarImg = document.querySelector(".teacher-avatar img.avatar-circle");
  const avatarDiv = document.querySelector(".teacher-avatar");

  // ✅ If no <img> exists (means initials are shown), try loading from stored profile
  if (!avatarImg && avatarDiv) {
    const storedUrl = localStorage.getItem("teacherProfileUrl");
    if (storedUrl) {
      avatarDiv.innerHTML = `<img src="${storedUrl}" alt="Profile Picture" class="avatar-circle">`;
    }
  }

  // ✅ If <img> exists but broken or empty, fallback to default
  if (avatarImg) {
    avatarImg.onerror = () => {
      avatarImg.src = defaultProfileUrl;
    };
    if (!avatarImg.src || avatarImg.src.trim() === "") {
      avatarImg.src = defaultProfileUrl;
    }
  }

  // ✅ When profile is updated (from upload JS)
  window.updateSidebarProfilePicture = function (newUrl) {
    const avatarImg = document.querySelector(".teacher-avatar img.avatar-circle");
    const avatarSpan = document.querySelector(".teacher-avatar span");

    if (avatarImg) {
      avatarImg.src = newUrl;
    } else if (avatarSpan) {
      const avatarDiv = document.querySelector(".teacher-avatar");
      avatarDiv.innerHTML = `<img src="${newUrl}" alt="Profile Picture" class="avatar-circle">`;
    }

    // Save to localStorage so it persists across pages
    localStorage.setItem("teacherProfileUrl", newUrl);
  };
});
