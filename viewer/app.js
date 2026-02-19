// viewer/app.js

function toChineseNum(num) {
    const changeNum = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
    num = parseInt(num);
    if (num > 1000) {
        return num.toString().split('').map(d => changeNum[d]).join('');
    } else if (num <= 10) {
        return changeNum[num];
    } else if (num < 20) {
        return '十' + (num % 10 === 0 ? '' : changeNum[num % 10]);
    } else {
        return changeNum[Math.floor(num / 10)] + '十' + (num % 10 === 0 ? '' : changeNum[num % 10]);
    }
}

async function loadCalendar() {
    const year = document.getElementById('yearInput').value;
    const month = parseInt(document.getElementById('monthInput').value);
    const grid = document.getElementById('calendar-grid');
    grid.innerHTML = ''; 

    try {
        const response = await fetch(`../output/${year}.json`);
        if (!response.ok) throw new Error('找不到文件');
        const data = await response.json();
        const entries = data.entries || data;
        renderMonth(year, month, entries, grid);
    } catch (error) {
        console.error(error);
        grid.innerHTML = `<p style="text-align:center;width:100%;color:#999">⚠️ 还没生成这年的胶囊数据哦</p>`;
    }
}

function renderMonth(year, month, entries, container) {
    const firstDayIndex = new Date(year, month - 1, 1).getDay();
    const daysInMonth = new Date(year, month, 0).getDate();

    for (let i = 0; i < firstDayIndex; i++) {
        const empty = document.createElement('div');
        empty.className = 'day-card empty-day';
        empty.style.cursor = 'default';
        container.appendChild(empty);
    }

    for (let day = 1; day <= daysInMonth; day++) {
        const dateKey = `${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const entry = entries[dateKey]; 

        const card = document.createElement('div');
        card.className = 'day-card';
        
        let htmlContent = `<div class="date-num">${day}</div>`;

        if (entry) {
            const tags = entry.tags || [];
            const type = entry.type || '';
            const meta = entry.meta || {};

            // ✨ 修复逻辑：不仅查 tags，也要查 type！
            
            // 1. 生日
            if (type === 'birthday' || tags.includes('birthday')) {
                htmlContent += `<div class="tag birthday">🎂 生日</div>`;
            } 
            // 2. 节日 (修复点：加上了 type === 'festival')
            else if (type === 'festival' || tags.includes('festival') || tags.includes('public_holiday')) {
                const tagName = meta.name ? meta.name : '节';
                htmlContent += `<div class="tag festival">${tagName}</div>`;
            } 
            // 3. 节气
            else if (type === 'solar_term' || tags.includes('solar_term')) {
                const tagName = meta.name ? meta.name : '气';
                htmlContent += `<div class="tag solar">${tagName}</div>`;
            }

            // 小蓝点提示
            if (entry.text && entry.text.length > 0) {
                htmlContent += `<div class="has-content-dot"></div>`;
            }

            // 点击事件
            card.onclick = () => openModal(year, month, day, entry);
        }

        card.innerHTML = htmlContent;
        container.appendChild(card);
    }
}

function openModal(year, month, day, entry) {
    const modal = document.getElementById('modal-overlay');
    const tagsContainer = document.getElementById('modal-tags');
    
    document.getElementById('modal-year').innerText = `${toChineseNum(year)}年`;
    document.getElementById('modal-date').innerText = `${toChineseNum(month)}月${toChineseNum(day)}日`;

    let tagsHtml = '';
    const meta = entry.meta || {};
    if (meta.name) tagsHtml += `<span>${meta.name}</span>`;
    if (entry.type === 'birthday') tagsHtml += `<span>🎂 Faye生日</span>`;
    tagsContainer.innerHTML = tagsHtml;

    const text = entry.text || "（这天没有留下寄语，也许是忙碌而充实的一天。）";
    document.getElementById('modal-text').innerText = text;

    modal.classList.remove('hidden');
    setTimeout(() => modal.classList.add('show'), 10);
}

function closeModal() {
    const modal = document.getElementById('modal-overlay');
    modal.classList.remove('show');
    setTimeout(() => modal.classList.add('hidden'), 300);
}

document.getElementById('modal-overlay').addEventListener('click', (e) => {
    if (e.target.id === 'modal-overlay') closeModal();
});

window.onload = loadCalendar;