document.addEventListener('DOMContentLoaded', () => {
    fetchFleet();

    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('action-modal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('action-modal')) closeModal();
    });
});

async function fetchFleet() {
    const grid = document.getElementById('fleet-grid');
    const status = document.getElementById('status-bar');

    try {
        const response = await fetch('/api/vehicles');
        if (!response.ok) throw new Error('Failed to fetch data');

        const data = await response.json();
        renderFleet(data.vehicles);
        status.innerHTML = `Loaded ${data.vehicles.length} vehicles from server.`;
        setTimeout(() => status.style.display = 'none', 3000);
    } catch (error) {
        status.innerHTML = `<span style="color: var(--danger)">Error connecting to server. Is python web_server.py running?</span>`;
        console.error(error);
    }
}

function renderFleet(vehicles) {
    const grid = document.getElementById('fleet-grid');
    grid.innerHTML = ''; 

    vehicles.forEach(v => {
        const card = document.createElement('div');
        card.className = `vehicle-card ${v.type.toLowerCase()}`;

        const isAvailable = v.is_available;
        const buttonHtml = isAvailable 
            ? `<button class="btn btn-rent" onclick="openRentModal('${v.vehicle_number}', '${v.brand}')">Rent Vehicle</button>`
            : `<button class="btn btn-return" onclick="openReturnModal('${v.vehicle_number}', '${v.brand}')">Return Vehicle</button>`;

        card.innerHTML = `
            <div class="v-header">
                <span class="v-type">${v.type}</span>
                <span class="v-number">${v.vehicle_number}</span>
            </div>
            <h3 class="v-brand">${v.brand}</h3>
            <p class="v-specs">${v.specs}</p>
            <p class="v-price">₹${v.price_per_day.toLocaleString()} <span>/ day</span></p>
            <div class="v-actions">
                ${buttonHtml}
            </div>
        `;
        grid.appendChild(card);
    });
}

const modal = document.getElementById('action-modal');
const modalTitle = document.getElementById('modal-title');
const modalContent = document.getElementById('modal-content');
const modalError = document.getElementById('modal-error');
const modalSuccess = document.getElementById('modal-success');

function closeModal() {
    modal.classList.remove('active');
    setTimeout(() => {
        modalError.innerText = '';
        modalSuccess.innerText = '';
    }, 300);
}

function openRentModal(vNum, vBrand) {
    modalTitle.innerText = `Rent ${vBrand}`;
    modalContent.innerHTML = `
        <div class="form-group">
            <label for="rent-days">Number of Days</label>
            <input type="number" id="rent-days" min="1" value="1">
        </div>
        <button class="btn btn-rent" onclick="processRent('${vNum}')" id="submit-btn">Confirm Rental</button>
    `;
    modalError.innerText = '';
    modalSuccess.innerText = '';
    modal.classList.add('active');
}

function openReturnModal(vNum, vBrand) {
    modalTitle.innerText = `Return ${vBrand}`;
    modalContent.innerHTML = `
        <p style="margin-bottom: 1.5rem; color: var(--text-muted)">Confirm that you want to return this vehicle.</p>
        <button class="btn btn-rent" onclick="processReturn('${vNum}')" id="submit-btn">Confirm Return</button>
    `;
    modalError.innerText = '';
    modalSuccess.innerText = '';
    modal.classList.add('active');
}

async function processRent(vNum) {
    const days = document.getElementById('rent-days').value;
    const btn = document.getElementById('submit-btn');

    modalError.innerText = '';
    modalSuccess.innerText = '';
    btn.disabled = true;
    btn.innerText = 'Processing...';

    try {
        const response = await fetch('/api/rent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vehicle_number: vNum, days: parseInt(days) })
        });

        const result = await response.json();
        if (!response.ok || !result.success) throw new Error(result.error || 'Failed to rent');

        modalSuccess.innerHTML = `${result.message}<br><strong>Total Charged: ₹${result.cost.toLocaleString()}</strong>`;
        btn.style.display = 'none';

        setTimeout(() => {
            closeModal();
            fetchFleet();
        }, 3000);

    } catch (error) {
        modalError.innerText = error.message;
        btn.disabled = false;
        btn.innerText = 'Confirm Rental';
    }
}

async function processReturn(vNum) {
    const btn = document.getElementById('submit-btn');

    modalError.innerText = '';
    modalSuccess.innerText = '';
    btn.disabled = true;
    btn.innerText = 'Processing...';

    try {
        const response = await fetch('/api/return', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vehicle_number: vNum })
        });

        const result = await response.json();
        if (!response.ok || !result.success) throw new Error(result.error || 'Failed to return');

        modalSuccess.innerText = result.message;
        btn.style.display = 'none';

        setTimeout(() => {
            closeModal();
            fetchFleet();
        }, 2000);

    } catch (error) {
        modalError.innerText = error.message;
        btn.disabled = false;
        btn.innerText = 'Confirm Return';
    }
}
