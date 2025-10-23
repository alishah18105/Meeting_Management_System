    document.querySelectorAll('.share-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const meetingId = btn.dataset.id;
            const formType = btn.dataset.type;

            try {
                const res = await fetch(`/form/share/${meetingId}/${formType}`);
                const data = await res.json();

                navigator.clipboard.writeText(data.share_url);
                alert(`✅ Share link copied!\n${data.share_url}`);
            } catch (err) {
                alert("Failed to generate share link.");
            }
        });
    });
    function openFormModal(btn) {
        let meetingId = btn.getAttribute("data-meeting-id");
        let formType = btn.getAttribute("data-form-type");

        let modalBody = document.getElementById("formModalBody");

        // Show modal
        let formModal = new bootstrap.Modal(document.getElementById('formModal'), {
            backdrop: false
        });
        formModal.show();

        // Show loading spinner
        modalBody.innerHTML = `
        <div class="text-center py-5" id="loadingSpinner">
            <div class="spinner-border text-light" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;

        // Fetch formFill.html from Flask
        fetch(`/forms/${meetingId}/${formType}`)
            .then(response => response.text())
            .then(html => {
                modalBody.innerHTML = html; // replace spinner with actual form
            })
            .catch(err => {
                modalBody.innerHTML = `<div class="text-danger text-center">Failed to load form.</div>`;
            });
    }

