document.addEventListener('DOMContentLoaded', function() {
    var eventSelect = document.getElementById('id_event');
    var schoolYearInput = document.getElementById('id_school_year');
    var yearInput = document.getElementById('id_year');
    var semesterSelect = document.getElementById('id_semester');

    if (eventSelect) {
        eventSelect.addEventListener('change', function() {
            var eventId = this.value;
            if (eventId) {
                fetch('/api/event-info/' + eventId + '/')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            if (schoolYearInput && data.school_year != null) {
                                schoolYearInput.value = data.school_year;
                            }
                            if (yearInput && data.year != null) {
                                yearInput.value = data.year;
                            }
                            if (semesterSelect && data.semester != null) {
                                semesterSelect.value = data.semester;
                            }
                        }
                    })
                    .catch(error => console.error('Error fetching event data:', error));
            }
        });
    }
});
