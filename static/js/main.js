/**
 * MediAssist - Frontend JavaScript
 * Symptom picker, body region browsing, drug interaction checker
 */

document.addEventListener('DOMContentLoaded', function() {
    initSymptomChecker();
    initDrugChecker();
});

/* ---------- Symptom Checker ---------- */

function initSymptomChecker() {
    const form = document.getElementById('symptom-form');
    if (!form) return;

    const checkboxes = form.querySelectorAll('.symptom-checkbox');
    const searchInput = document.getElementById('symptom-search');
    const selectedContainer = document.getElementById('selected-symptoms');
    const checkBtn = document.getElementById('check-btn');
    const regionButtons = document.querySelectorAll('.body-region-btn');
    const regionGroups = document.querySelectorAll('.symptom-region-group');

    // Symptom checkbox change handler
    checkboxes.forEach(function(cb) {
        cb.addEventListener('change', function() {
            var severitySelect = this.closest('.symptom-item').querySelector('.severity-select');
            if (severitySelect) {
                severitySelect.disabled = !this.checked;
            }
            updateSelectedSymptoms();
        });
    });

    // Search filter
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            var query = this.value.toLowerCase().trim();
            var items = form.querySelectorAll('.symptom-item');
            items.forEach(function(item) {
                var name = item.getAttribute('data-name') || '';
                if (!query || name.indexOf(query) !== -1) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
            // Show all region groups when searching
            regionGroups.forEach(function(g) { g.style.display = ''; });
            regionButtons.forEach(function(b) { b.classList.remove('active'); });
        });
    }

    // Body region buttons
    regionButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var region = this.getAttribute('data-region');

            regionButtons.forEach(function(b) { b.classList.remove('active'); });
            this.classList.add('active');

            regionGroups.forEach(function(group) {
                if (group.getAttribute('data-region') === region) {
                    group.style.display = '';
                } else {
                    group.style.display = 'none';
                }
            });

            // Clear search
            if (searchInput) searchInput.value = '';
        });
    });

    function updateSelectedSymptoms() {
        var selected = [];
        checkboxes.forEach(function(cb) {
            if (cb.checked) selected.push(cb.value);
        });

        if (selected.length === 0) {
            selectedContainer.innerHTML = '<p class="empty-state">No symptoms selected yet.</p>';
            checkBtn.disabled = true;
        } else {
            var html = '';
            selected.forEach(function(name) {
                html += '<span class="selected-tag">' + escapeHtml(name) + '</span>';
            });
            selectedContainer.innerHTML = html;
            checkBtn.disabled = false;
        }
    }
}

/* ---------- Drug Interaction Checker ---------- */

function initDrugChecker() {
    var checkBtn = document.getElementById('check-interactions-btn');
    if (!checkBtn) return;

    var drugCheckboxes = document.querySelectorAll('.drug-checkbox');
    var searchInput = document.getElementById('drug-search');
    var selectedContainer = document.getElementById('selected-drugs');
    var resultsContainer = document.getElementById('interaction-results');
    var listContainer = document.getElementById('interaction-list');

    // Drug checkbox handler
    drugCheckboxes.forEach(function(cb) {
        cb.addEventListener('change', updateSelectedDrugs);
    });

    // Search filter
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            var query = this.value.toLowerCase().trim();
            var items = document.querySelectorAll('.drug-item');
            items.forEach(function(item) {
                var name = item.getAttribute('data-name') || '';
                if (!query || name.indexOf(query) !== -1) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // Check interactions button
    checkBtn.addEventListener('click', function() {
        var selectedIds = [];
        drugCheckboxes.forEach(function(cb) {
            if (cb.checked) selectedIds.push(parseInt(cb.value));
        });

        if (selectedIds.length < 2) return;

        checkBtn.disabled = true;
        checkBtn.textContent = 'Checking...';

        fetch('/api/interactions/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drug_ids: selectedIds })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            displayInteractions(data.interactions || []);
            checkBtn.disabled = false;
            checkBtn.textContent = 'Check Interactions';
        })
        .catch(function(err) {
            listContainer.innerHTML = '<p class="alert alert-danger">Error checking interactions.</p>';
            resultsContainer.style.display = 'block';
            checkBtn.disabled = false;
            checkBtn.textContent = 'Check Interactions';
        });
    });

    function updateSelectedDrugs() {
        var selected = [];
        drugCheckboxes.forEach(function(cb) {
            if (cb.checked) {
                selected.push({
                    id: cb.value,
                    name: cb.getAttribute('data-drug-name')
                });
            }
        });

        if (selected.length === 0) {
            selectedContainer.innerHTML = '<p class="empty-state">Select at least 2 medications to check interactions.</p>';
            checkBtn.disabled = true;
        } else {
            var html = '';
            selected.forEach(function(d) {
                html += '<span class="selected-tag">' + escapeHtml(d.name) + '</span>';
            });
            selectedContainer.innerHTML = html;
            checkBtn.disabled = selected.length < 2;
        }

        // Hide previous results when selection changes
        resultsContainer.style.display = 'none';
    }

    function displayInteractions(interactions) {
        if (interactions.length === 0) {
            listContainer.innerHTML = '<div class="alert" style="background:#d4edda;color:#155724;border:1px solid #c3e6cb;">' +
                '<strong>No interactions found.</strong> The selected medications do not have known interactions in our database.</div>';
        } else {
            var html = '<p style="margin-bottom:12px;font-weight:500;">' + interactions.length + ' interaction(s) found:</p>';
            interactions.forEach(function(ix) {
                var severity = ix.severity || 'minor';
                var drugAName = ix.drug_a ? ix.drug_a.name : 'Unknown';
                var drugBName = ix.drug_b ? ix.drug_b.name : 'Unknown';
                html += '<div class="interaction-card severity-' + severity + '">';
                html += '<div class="interaction-severity">' + severity + '</div>';
                html += '<div class="interaction-drugs">' + escapeHtml(drugAName) + ' + ' + escapeHtml(drugBName) + '</div>';
                html += '<div class="interaction-desc">' + escapeHtml(ix.description || '') + '</div>';
                if (ix.recommendation) {
                    html += '<div class="interaction-rec">Recommendation: ' + escapeHtml(ix.recommendation) + '</div>';
                }
                html += '</div>';
            });
        }
        listContainer.innerHTML = html;
        resultsContainer.style.display = 'block';
    }
}

/* ---------- Utility ---------- */

function escapeHtml(text) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}
