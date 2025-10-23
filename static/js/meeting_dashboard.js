document.addEventListener("DOMContentLoaded", function () {
      // Apply saved theme from localStorage
      const savedTheme = localStorage.getItem("theme") || "light-theme";
      document.body.classList.remove("light-theme", "grey-theme", "dark-theme");
      document.body.classList.add(savedTheme);
    });

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("meetingSearch");
  const dropdown = document.getElementById("meetingDropdown");
  let meetings = [];

  async function loadMeetings() {
    try {
      const res = await fetch("/get_user_meetings");
      meetings = await res.json();
    } catch (err) {
      console.error("Error fetching meetings:", err);
    }
  }

  function renderDropdown(query = "") {
    const filtered = meetings.filter(m =>
      m.title.toLowerCase().includes(query.toLowerCase())
    );

    dropdown.innerHTML = "";

    if (filtered.length === 0) {
      dropdown.style.display = "none";
      return;
    }

    filtered.forEach(m => {
      const item = document.createElement("a");
      item.href = `/search?meeting_id=${encodeURIComponent(m.meeting_id)}`;
      item.className = "dropdown-item";
      item.textContent = m.title;
      dropdown.appendChild(item);
    });

    dropdown.style.display = "block";
  }

  // On focus → show all meetings
  input.addEventListener("focus", () => {
    if (meetings.length > 0) renderDropdown();
    else loadMeetings().then(() => renderDropdown());
  });

  // On input → filter meetings
  input.addEventListener("input", () => {
    const query = input.value.trim();
    renderDropdown(query);
  });

  // Hide dropdown when clicking outside
  document.addEventListener("click", (e) => {
    if (!e.target.closest("form")) {
      dropdown.style.display = "none";
    }
  });

  // Preload meeting data early (optional)
  loadMeetings();
});