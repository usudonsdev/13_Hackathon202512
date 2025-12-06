// script.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('Smart Scheduler initialized');

    // --- DOM Elements ---
    const btnTodayTodo = document.getElementById('btn-today-todo');
    const btnFriends = document.getElementById('btn-friends');
    const btnLlm = document.getElementById('btn-llm');
    const calendarGrid = document.getElementById('calendar-grid');
    const eventModal = document.getElementById('event-modal');
    const friendModal = document.getElementById('friend-modal');

    // --- State ---
    let currentDate = new Date();

    // --- Event Listeners ---

    // Navigation interaction placeholders
    btnTodayTodo.addEventListener('click', () => {
        alert('今日やること機能は実装中です');
    });

    btnFriends.addEventListener('click', () => {
        openModal(friendModal);
    });

    btnLlm.addEventListener('click', () => {
        alert('LLM機能は実装中です');
    });

    // Calendar Interactions (Placeholder)
    // In a real implementation, clicking a time slot would open the event modal
    calendarGrid.addEventListener('click', () => {
        // Only for demo purposes: if grid is clicked, show event modal
        // In reality, check for specific cell target
        // openModal(eventModal);
    });

    // Modal Controls
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            closeModal(modal);
        });
    });

    // Quick Event Creation (Demo)
    // To demonstrate input specs
    document.getElementById('event-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const title = document.getElementById('event-title').value;
        const start = document.getElementById('event-start').value;
        const end = document.getElementById('event-end').value;
        const visibility = document.querySelector('input[name="visibility"]:checked').value;
        const memo = document.getElementById('event-memo').value;

        console.log('New Event:', { title, start, end, visibility, memo });

        // Save to localStorage logic would go here

        closeModal(eventModal);
        alert(`予定「${title}」を保存しました`);
    });

    // --- Functions ---

    function openModal(modal) {
        modal.classList.remove('hidden');
    }

    function closeModal(modal) {
        modal.classList.add('hidden');
    }

    function renderCalendar() {
        // Placeholder for calendar rendering logic
        calendarGrid.innerHTML = `
            <div style="padding: 2rem; width: 100%; text-align: center;">
                <h3>${currentDate.toLocaleDateString()} の週（仮表示）</h3>
                <p>ここにカレンダーが描画されます</p>
                <button onclick="document.getElementById('event-modal').classList.remove('hidden')">
                    予定追加テスト
                </button>
            </div>
        `;
    }

    // Initialize
    renderCalendar();
});
