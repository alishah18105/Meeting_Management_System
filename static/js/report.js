document.addEventListener("DOMContentLoaded", function () {
        const reportType = document.getElementById("reportType");
        const titleSelect = document.getElementById("title");
        const startDate = document.getElementById("startDate");
        const endDate = document.getElementById("endDate");
        const statusButton = document.querySelector(".dropdown-toggle");
        const statusMenu = document.querySelector(".dropdown-menu");
        const statusChecks = document.querySelectorAll("input[name='status']");

        // 🔹 Normal disable for inputs & selects
        function disableField(el) {
            el.disabled = true;
            el.style.pointerEvents = "none";
            el.style.opacity = "0.6";
            el.style.backgroundColor = "#e9ecef";
            el.classList.add("disabled-select");
        }

        function enableField(el) {
            el.disabled = false;
            el.style.pointerEvents = "auto";
            el.style.opacity = "1";
            el.style.backgroundColor = "white";
            el.classList.remove("disabled-select");
        }

        // 🔹 Special handling for Bootstrap dropdown
        function disableDropdown() {
            statusButton.classList.add("disabled-dropdown");
            statusButton.style.pointerEvents = "none";
            statusButton.style.opacity = "0.6";
            statusButton.style.cursor = "not-allowed";
            statusButton.removeAttribute("data-bs-toggle"); // Prevent open
            statusMenu.classList.add("d-none"); // Hide dropdown items
            statusChecks.forEach(c => (c.disabled = true));
        }

        function enableDropdown() {
            statusButton.classList.remove("disabled-dropdown");
            statusButton.style.pointerEvents = "auto";
            statusButton.style.opacity = "1";
            statusButton.style.cursor = "pointer";
            statusButton.setAttribute("data-bs-toggle", "dropdown");
            statusMenu.classList.remove("d-none");
            statusChecks.forEach(c => (c.disabled = false));
        }

        // 🔹 Main toggle logic
        function toggleFields() {
            const selected = reportType.value;

            if (selected === "Participant_Report") {
                // ✅ Only meeting title active
                enableField(titleSelect);
                disableField(startDate);
                disableField(endDate);
                disableDropdown();
            }
            else if (selected === "Meeting_Summary") {
                // ✅ Dates and status active, title disabled
                enableField(titleSelect);
                enableField(startDate);
                enableField(endDate);
                enableDropdown();
            }

            else if (selected == "Room_Utilization_Report") {
                disableField(titleSelect);
                disableDropdown();
                enableField(startDate);
                enableField(endDate);
            }
            else {
                // ✅ Everything enabled (default)
                enableField(titleSelect);
                enableField(startDate);
                enableField(endDate);
                enableDropdown();
            }
        }

        // 🔹 Run on load + on change
        toggleFields();
        reportType.addEventListener("change", toggleFields);
    });
    document.addEventListener('DOMContentLoaded', function () {
        const addSummaryModal = document.getElementById('addSummaryModal');

        addSummaryModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const meetingId = button.getAttribute('data-meeting-id');
            const meetingTitle = button.getAttribute('data-meeting-title');
            let meetingSummary = button.getAttribute('data-meeting-summary');

            // Fix for apostrophes or special characters
            if (meetingSummary)
                meetingSummary = meetingSummary.replace(/&apos;/g, "'").replace(/&#39;/g, "'");

            // Fill modal fields
            document.getElementById('modalMeetingId').value = meetingId;
            document.getElementById('modalMeetingTitle').value = meetingTitle;
            document.getElementById('modalMeetingSummary').value =
                meetingSummary && meetingSummary !== 'No summary added yet' &&
                    meetingSummary !== "You haven't added a summary yet"
                    ? meetingSummary
                    : '';
        });
    });
    function deleteMeeting(event, form) {
        event.preventDefault();

        const meetingId = form.getAttribute('data-meeting-id');

        if (confirm("Are you sure you want to delete this meeting?")) {
            fetch(`/delete_meeting/${meetingId}`, {
                method: 'POST'
            })
            .then(response => {
                if (response.ok) {
                    alert("Meeting deleted successfully!");
                    location.reload();
                } else {
                    alert("Failed to delete meeting.");
                }
            })
            .catch(error => console.error('Error:', error));
        }
    }