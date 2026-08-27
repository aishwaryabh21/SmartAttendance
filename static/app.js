function updateClock() {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  const ss = String(now.getSeconds()).padStart(2, '0');
  document.getElementById('clock').textContent = `${hh}:${mm}:${ss}`;
}
setInterval(updateClock, 1000);
updateClock();

function renderRoster(data) {
  document.getElementById('stat-total').textContent = data.total;
  document.getElementById('stat-present').textContent = data.present;
  document.getElementById('stat-absent').textContent = data.absent;

  const roster = document.getElementById('roster');

  if (!data.students || data.students.length === 0) {
    roster.innerHTML = '<div class="empty-state">No students enrolled yet. Run train_recognizer.py first.</div>';
    return;
  }

  roster.innerHTML = data.students.map((s, i) => {
    const idNum = String(i + 1).padStart(2, '0');
    const isPresent = s.status === 'Present';
    const statusClass = isPresent ? 'present' : 'absent';
    const statusLabel = isPresent ? 'PRESENT' : 'ABSENT';
    const time = s.timestamp ? s.timestamp : '--:--:--';

    return `
      <div class="roster-row">
        <span class="roster-id">${idNum}</span>
        <span class="roster-name">${escapeHtml(s.name)}</span>
        <span class="status-pill ${statusClass}">
          <span class="status-dot"></span>${statusLabel}
        </span>
        <span class="roster-time">${time}</span>
      </div>
    `;
  }).join('');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

async function pollStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    renderRoster(data);
  } catch (err) {
    console.error('Failed to fetch attendance status:', err);
  }
}

pollStatus();
setInterval(pollStatus, 2000);
