document.addEventListener("DOMContentLoaded", () => {
    lucide.createIcons();

  const defaultProfileUrl =
    "https://qimrryerxdzfewbkoqyq.supabase.co/storage/v1/object/public/ProfilePicture/avatar.png";

  const avatarImg = document.querySelector(".student-avatar img.avatar-circle");
  const avatarDiv = document.querySelector(".student-avatar");

  if (!avatarImg && avatarDiv) {
    const storedUrl = localStorage.getItem("studentProfileUrl");
    if (storedUrl) {
      avatarDiv.innerHTML = `<img src="${storedUrl}" alt="Profile Picture" class="avatar-circle">`;
    }
  }

  if (avatarImg) {
    avatarImg.onerror = () => {
      avatarImg.src = defaultProfileUrl;
    };
    if (!avatarImg.src || avatarImg.src.trim() === "") {
      avatarImg.src = defaultProfileUrl;
    }
  }

  window.updateSidebarProfilePicture = function (newUrl) {
    const avatarImg = document.querySelector(".student-avatar img.avatar-circle");
    const avatarSpan = document.querySelector(".student-avatar span");

    if (avatarImg) {
      avatarImg.src = newUrl;
    } else if (avatarSpan) {
      const avatarDiv = document.querySelector(".student-avatar");
      avatarDiv.innerHTML = `<img src="${newUrl}" alt="Profile Picture" class="avatar-circle">`;
    }

    localStorage.setItem("studentProfileUrl", newUrl);
  };
});
