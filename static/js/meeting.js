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
  function startMeeting(meetingTitleFromCard = null) {
  let meetingTitle = meetingTitleFromCard;

  if (!meetingTitle) {
    const modalElement = document.getElementById('instantMeetingModal');
    const titleInput = modalElement ? modalElement.querySelector('input[name="title"]') : null;
    meetingTitle = titleInput ? titleInput.value.trim() : "";
  }

  if (!meetingTitle) {
    alert("Please enter a meeting title before starting.");
    return;
  }

  const modalElement = document.getElementById('instantMeetingModal');
  const modal = bootstrap.Modal.getInstance(modalElement);
  if (modal) modal.hide();

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
  const roomName = meetingTitle.replace(/\s+/g, "_") + "_" + Date.now();

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
      requireDisplayName: false,
      lobby: { enable: false }
    },
    interfaceConfigOverwrite: {
      SHOW_JITSI_WATERMARK: false,
      SHOW_WATERMARK_FOR_GUESTS: false,
      TOOLBAR_BUTTONS: [
        'microphone', 'camera', 'chat', 'raisehand',
        'tileview', 'hangup', 'desktop', 'fullscreen', 'participants-pane'
      ],
    },
    userInfo: {
       displayName: currentUserName || "Host"
    }
  };

  const api = new JitsiMeetExternalAPI(domain, options);

  // ✅ Handle meeting close
  api.addEventListener('readyToClose', () => {
    api.dispose();
    container.remove();
    window.location.href = "/meeting";
  });
}

  document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.join-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (btn.classList.contains('disabled')) return;
      const meetingTitle = btn.getAttribute('data-title');
      startMeeting(meetingTitle);
    });
  });
});

