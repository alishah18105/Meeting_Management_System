document.addEventListener("DOMContentLoaded", function () {
    const shareButtons = document.querySelectorAll(".share-btn");
    const shareModal = new bootstrap.Modal(document.getElementById("shareMeetingModal"));
    const shareTextArea = document.getElementById("shareText");
    const copyBtn = document.getElementById("copyShareText");

    shareButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.meetingId;
        const title = btn.dataset.title;
        const start = btn.dataset.start;
        const end = btn.dataset.end;

        const startTime = new Date(start);
        const endTime = new Date(end);
        const duration = ((endTime - startTime) / (1000 * 60 * 60)).toFixed(1) + " hrs";

        const text = `Meeting ID: ${id}\nTitle: ${title}\nStart Time: ${start}\nDuration: ${duration}`;
        shareTextArea.value = text;

        shareModal.show();
      });
    });

    copyBtn.addEventListener("click", () => {
      shareTextArea.select();
      document.execCommand("copy");
      copyBtn.textContent = "Copied!";
      setTimeout(() => (copyBtn.textContent = "Copy"), 1500);
    });
  });



  document.addEventListener('DOMContentLoaded', function () {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(el => new bootstrap.Tooltip(el));
  });
  
  
  function startMeeting(meetingTitle, meetingId, role) {
  if (!meetingTitle) {
    alert("Meeting title not found.");
    return;
  }

  const container = document.createElement('div');
  container.id = 'jitsiContainer';
  Object.assign(container.style, {
    position: 'fixed',
    top: '0',
    left: '0',
    width: '100vw',
    height: '100vh',
    zIndex: '9999'
  });
  document.body.appendChild(container);

  const domain = "jitsi.riot.im";
  const roomName = meetingTitle.replace(/\s+/g, "_") + "_" + meetingId;

  // 🧩 Host has full toolbar; participants have limited controls
  const hostToolbar = [
    'microphone', 'camera', 'chat', 'raisehand',
    'tileview', 'hangup', 'desktop', 'fullscreen', 'participants-pane', 'mute-everyone'
  ];

  const participantToolbar = [
    'microphone', 'camera', 'chat', 'raisehand', 'tileview', 'hangup'
  ];

  const options = {
    roomName: roomName,
    parentNode: container,
    width: "100%",
    height: "100%",
    configOverwrite: {
      disableDeepLinking: true,
      prejoinPageEnabled: false,
      enableLobby: false,
      enableWelcomePage: false,
      requireDisplayName: false
    },
    interfaceConfigOverwrite: {
      SHOW_JITSI_WATERMARK: false,
      SHOW_WATERMARK_FOR_GUESTS: false,
      TOOLBAR_BUTTONS: role === "host" ? hostToolbar : participantToolbar,
    },
    userInfo: {
      displayName: currentUserName || (role === "host" ? "Host" : "Participant")
    }
  };

  const api = new JitsiMeetExternalAPI(domain, options);

  // ✅ Only host can end the meeting for everyone
  if (role === "host") {
    api.addEventListener('readyToClose', () => {
      api.dispose();
      container.remove();
      window.location.href = "/meeting";
    });
  } else {
    api.addEventListener('readyToClose', () => {
      api.dispose();
      container.remove();
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.join-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (btn.classList.contains('disabled')) return;
      const meetingTitle = btn.getAttribute('data-title');
      const meetingId = btn.getAttribute('data-id');
      const role = btn.getAttribute('data-role');
      startMeeting(meetingTitle, meetingId, role);
    });
  });
});



