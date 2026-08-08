class Vehicle {
  constructor(type, number, brand, basePrice, isAvailable = true, currentRental = null) {
    this.type = type;
    this.number = number;
    this.brand = brand;
    this.basePrice = parseFloat(basePrice);
    this.isAvailable = isAvailable;
    this.currentRental = currentRental;
  }

  applyLongTermDiscount(total, days) {
    return days > 7 ? total * 0.9 : total;
  }

  latePenalty(actualDays, plannedDays) {
    const extra = Math.max(0, actualDays - plannedDays);
    return extra * this.basePrice * 0.2; 
  }
}

class Car extends Vehicle {
  constructor(number, brand, basePrice, seats, isAvailable, currentRental) {
    super('Car', number, brand, basePrice, isAvailable, currentRental);
    this.seats = parseInt(seats);
  }

  calculateRental(days) {
    const extraSeats = Math.max(0, this.seats - 4);
    const surcharge = extraSeats * 100;
    const daily = this.basePrice + surcharge;
    return this.applyLongTermDiscount(daily * days, days);
  }
}

class Bike extends Vehicle {
  constructor(number, brand, basePrice, engineCC, isAvailable, currentRental) {
    super('Bike', number, brand, basePrice, isAvailable, currentRental);
    this.engineCC = parseInt(engineCC);
  }

  calculateRental(days) {
    const surcharge = this.engineCC > 150 ? 50 : 0;
    const daily = this.basePrice + surcharge;
    return this.applyLongTermDiscount(daily * days, days);
  }
}

class RentalSystem {
  constructor() {
    this.fleet = [];
    this.history = {}; 
    this.transactions = [];
    this.loadData();
  }

  loadData() {
    const data = JSON.parse(localStorage.getItem('vehicleRentalData'));
    if (data && data.fleet.length > 0) {
      this.fleet = data.fleet.map(v => {
        if (v.type === 'Car') return new Car(v.number, v.brand, v.basePrice, v.seats, v.isAvailable, v.currentRental);
        return new Bike(v.number, v.brand, v.basePrice, v.engineCC, v.isAvailable, v.currentRental);
      });
      this.history = data.history || {};
      this.transactions = data.transactions || [];
    } else {
      this.seedData();
    }
  }

  saveData() {
    localStorage.setItem('vehicleRentalData', JSON.stringify({
      fleet: this.fleet,
      history: this.history,
      transactions: this.transactions
    }));
  }

  seedData() {
    this.fleet = [
      new Car('KA-01-AB-1234', 'Maruti Swift', 800, 5, true, null),
      new Car('MH-12-CD-5678', 'Toyota Innova', 1500, 8, true, null),
      new Car('DL-03-EF-0011', 'Hyundai Creta', 1200, 5, false, { renter: 'Rahul Sharma', days: 5, date: new Date().toISOString().split('T')[0] }),
      new Bike('DL-05-GH-9012', 'Honda Activa 6G', 200, 110, true, null),
      new Bike('TN-09-IJ-3456', 'KTM Duke 200', 400, 200, true, null),
    ];
    this.history = { 'Rahul Sharma': 1 };
    this.transactions = [{ type: 'Rent', vehicle: 'DL-03-EF-0011', renter: 'Rahul Sharma', date: new Date().toLocaleDateString(), amount: 0 }];
    this.saveData();
  }

  addVehicle(vehicle) {
    if (this.fleet.find(v => v.number === vehicle.number)) throw new Error('Vehicle number already exists.');
    this.fleet.push(vehicle);
    this.saveData();
  }

  rentVehicle(number, renter, days, startDate) {
    const vehicle = this.fleet.find(v => v.number === number);
    if (!vehicle) throw new Error('Vehicle not found.');
    if (!vehicle.isAvailable) throw new Error('Vehicle is not available.');

    let gross = vehicle.calculateRental(days);
    const hasLoyalty = (this.history[renter] || 0) > 0;
    const final = hasLoyalty ? gross * 0.95 : gross;

    vehicle.isAvailable = false;
    vehicle.currentRental = { renter, days, date: startDate };
    this.history[renter] = (this.history[renter] || 0) + 1;

    this.transactions.unshift({ type: 'Rent', vehicle: number, renter, date: new Date().toLocaleDateString(), amount: final });
    this.saveData();
    return final;
  }

  returnVehicle(number, actualDays) {
    const vehicle = this.fleet.find(v => v.number === number);
    if (!vehicle || vehicle.isAvailable) throw new Error('Vehicle not rented.');

    const rental = vehicle.currentRental;
    actualDays = actualDays || rental.days;

    let gross = vehicle.calculateRental(actualDays);
    const hasLoyalty = (this.history[rental.renter] || 0) > 1; 
    const finalRent = hasLoyalty ? gross * 0.95 : gross;
    const penalty = vehicle.latePenalty(actualDays, rental.days);
    const total = finalRent + penalty;

    this.transactions.unshift({ type: 'Return', vehicle: number, renter: rental.renter, date: new Date().toLocaleDateString(), amount: total });

    vehicle.isAvailable = true;
    vehicle.currentRental = null;
    this.saveData();

    return { finalRent, penalty, total, renter: rental.renter };
  }

  getRevenue() {
    return this.transactions.filter(t => t.type === 'Return').reduce((sum, t) => sum + t.amount, 0);
  }
}

const sys = new RentalSystem();

document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));

    const target = e.currentTarget;
    target.classList.add('active');
    document.getElementById(`section-${target.dataset.section}`).classList.add('active');
    document.getElementById('pageTitle').innerText = target.querySelector('.nav-label').innerText;

    if (window.innerWidth <= 768) document.getElementById('sidebar').classList.remove('open');
    refreshUI();
  });
});

document.getElementById('menuToggle').addEventListener('click', () => {
  document.getElementById('sidebar').classList.toggle('open');
});

function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span style="font-size: 20px;">${type === 'success' ? '✅' : '⚠️'}</span> ${message}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

const formatRs = (val) => '₹' + val.toLocaleString('en-IN', { maximumFractionDigits: 0 });

function renderFleet(filter = 'all', searchQuery = '') {
  const grid = document.getElementById('vehiclesGrid');
  grid.innerHTML = '';

  let list = sys.fleet;
  if (filter === 'car') list = list.filter(v => v.type === 'Car');
  else if (filter === 'bike') list = list.filter(v => v.type === 'Bike');
  else if (filter === 'available') list = list.filter(v => v.isAvailable);
  else if (filter === 'rented') list = list.filter(v => !v.isAvailable);

  if (searchQuery) {
    const q = searchQuery.toLowerCase();
    list = list.filter(v => v.brand.toLowerCase().includes(q) || v.number.toLowerCase().includes(q));
  }

  if (list.length === 0) {
    document.getElementById('fleetEmpty').classList.remove('hidden');
  } else {
    document.getElementById('fleetEmpty').classList.add('hidden');
    list.forEach(v => {
      const extra = v.type === 'Car' ? `${v.seats} Seats` : `${v.engineCC} CC`;
      const icon = v.type === 'Car' ? '🚗' : '🏍️';
      grid.innerHTML += `
        <div class="vehicle-card">
          <div class="vc-header">
            <span class="vc-type-icon">${icon}</span>
            <span class="vc-status ${v.isAvailable ? 'status-available' : 'status-rented'}">
              ${v.isAvailable ? 'Available' : 'Rented'}
            </span>
          </div>
          <div class="vc-brand">${v.brand}</div>
          <div class="vc-number">${v.number}</div>
          <div class="vc-details">
            <div class="vc-detail-row"><span>Type Detail</span><strong>${extra}</strong></div>
            ${!v.isAvailable ? `<div class="vc-detail-row"><span>Rented By</span><strong>${v.currentRental.renter}</strong></div>` : ''}
          </div>
          <div class="vc-price">${formatRs(v.basePrice)} <span style="font-size:12px; color:var(--text-muted); font-weight:normal;">/ day</span></div>
        </div>
      `;
    });
  }
}

function refreshUI() {

  document.getElementById('stat-total').innerText = sys.fleet.length;
  const avail = sys.fleet.filter(v => v.isAvailable).length;
  document.getElementById('stat-available').innerText = avail;
  document.getElementById('stat-rented').innerText = sys.fleet.length - avail;
  document.getElementById('availableCount').innerText = avail;
  document.getElementById('stat-revenue').innerText = formatRs(sys.getRevenue());

  const dAvail = document.getElementById('dashAvailable');
  dAvail.innerHTML = sys.fleet.filter(v => v.isAvailable).slice(0,3).map(v => `
    <div class="list-item">
      <div>
        <div class="list-item-title">${v.brand}</div>
        <div class="list-item-sub">${v.number}</div>
      </div>
      <div style="color:var(--primary-cyan); font-weight:600;">${formatRs(v.basePrice)}/d</div>
    </div>
  `).join('') || '<div class="list-item-sub" style="padding:10px;">None available</div>';

  const dRented = document.getElementById('dashRented');
  dRented.innerHTML = sys.fleet.filter(v => !v.isAvailable).slice(0,3).map(v => `
    <div class="list-item">
      <div>
        <div class="list-item-title">${v.brand}</div>
        <div class="list-item-sub">${v.currentRental.renter}</div>
      </div>
      <div class="badge-loyal">Due in ${v.currentRental.days}d</div>
    </div>
  `).join('') || '<div class="list-item-sub" style="padding:10px;">None rented</div>';

  const dRenters = document.getElementById('dashRenters');
  dRenters.innerHTML = Object.entries(sys.history).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([name, count]) => `
    <div class="list-item">
      <div>
        <div class="list-item-title">${name} ${count > 1 ? '<span class="badge-loyal">Loyal</span>' : ''}</div>
      </div>
      <div style="font-weight:600;">${count} rentals</div>
    </div>
  `).join('');

  renderFleet(document.querySelector('.filter-btn.active').dataset.filter, document.getElementById('globalSearch').value);

  const rentSel = document.getElementById('rentVehicleSelect');
  rentSel.innerHTML = '<option value="">— Choose an available vehicle —</option>' + 
    sys.fleet.filter(v => v.isAvailable).map(v => `<option value="${v.number}">${v.brand} (${v.number})</option>`).join('');

  const retSel = document.getElementById('returnVehicleSelect');
  retSel.innerHTML = '<option value="">— Choose a rented vehicle —</option>' + 
    sys.fleet.filter(v => !v.isAvailable).map(v => `<option value="${v.number}">${v.brand} (${v.number}) - ${v.currentRental.renter}</option>`).join('');

  document.getElementById('transactionList').innerHTML = sys.transactions.map(t => `
    <div class="list-item">
      <div>
        <div class="list-item-title">${t.type} - ${t.vehicle}</div>
        <div class="list-item-sub">${t.date} | ${t.renter}</div>
      </div>
      <div style="font-weight:600; color:${t.type==='Rent'?'var(--text-main)':'var(--success)'};">${t.amount > 0 ? formatRs(t.amount) : '-'}</div>
    </div>
  `).join('') || '<div class="list-item-sub" style="padding:10px;">No transactions yet.</div>';

  document.getElementById('renterLeaderboard').innerHTML = Object.entries(sys.history).sort((a,b)=>b[1]-a[1]).map(([name, count]) => `
    <div class="list-item">
      <div><span class="list-item-title">${name}</span> ${count > 1 ? '<span class="badge-loyal">Loyal Customer (5% off)</span>' : ''}</div>
      <div style="font-weight:600;">${count} rentals</div>
    </div>
  `).join('');
}

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    refreshUI();
  });
});
document.getElementById('globalSearch').addEventListener('input', refreshUI);

document.querySelectorAll('.type-toggle').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('.type-toggle').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    const type = e.target.dataset.type;
    document.getElementById('carField').classList.toggle('hidden', type !== 'Car');
    document.getElementById('bikeField').classList.toggle('hidden', type !== 'Bike');
  });
});

document.getElementById('addSubmitBtn').addEventListener('click', () => {
  const type = document.querySelector('.type-toggle.active').dataset.type;
  const num = document.getElementById('addVehicleNum').value.trim();
  const brand = document.getElementById('addBrand').value.trim();
  const price = document.getElementById('addBasePrice').value;

  try {
    if(!num || !brand || !price) throw new Error("All base fields required.");
    let vehicle;
    if (type === 'Car') {
      const seats = document.getElementById('addSeats').value;
      if(!seats) throw new Error("Seats required.");
      vehicle = new Car(num, brand, price, seats, true, null);
    } else {
      const cc = document.getElementById('addEngineCC').value;
      if(!cc) throw new Error("Engine CC required.");
      vehicle = new Bike(num, brand, price, cc, true, null);
    }
    sys.addVehicle(vehicle);
    showToast(`Vehicle ${num} added successfully!`);
    document.querySelectorAll('#section-add input').forEach(i => i.value = '');
    document.getElementById('nav-fleet').click();
  } catch(e) { showToast(e.message, 'error'); }
});

document.getElementById('rentVehicleSelect').addEventListener('change', (e) => {
  const val = e.target.value;
  const v = sys.fleet.find(x => x.number === val);
  const prev = document.getElementById('rentPreview');
  if(v) {
    prev.classList.remove('hidden');
    document.getElementById('rentPreviewCard').innerHTML = `
      <strong>${v.brand}</strong><br/>
      <span style="color:var(--text-muted);font-size:13px;">${v.type === 'Car'? v.seats+' Seats' : v.engineCC+' CC'} | Base: ${formatRs(v.basePrice)}/day</span>
    `;
    document.getElementById('rentStartDate').valueAsDate = new Date();
  } else { prev.classList.add('hidden'); }
});

document.getElementById('rentSubmitBtn').addEventListener('click', () => {
  const num = document.getElementById('rentVehicleSelect').value;
  const renter = document.getElementById('rentRenterName').value.trim();
  const days = parseInt(document.getElementById('rentDays').value);
  const date = document.getElementById('rentStartDate').value;

  try {
    if(!num || !renter || !days || !date) throw new Error("All fields required.");
    const cost = sys.rentVehicle(num, renter, days, date);
    showToast(`Success! Rented to ${renter}. Est cost: ${formatRs(cost)}`);
    document.querySelectorAll('#section-rent input, #section-rent select').forEach(i => i.value = '');
    document.getElementById('rentPreview').classList.add('hidden');
    document.getElementById('nav-dashboard').click();
  } catch(e) { showToast(e.message, 'error'); }
});

document.getElementById('returnSubmitBtn').addEventListener('click', () => {
  const num = document.getElementById('returnVehicleSelect').value;
  const actualDays = parseInt(document.getElementById('returnActualDays').value) || null;

  try {
    if(!num) throw new Error("Select a vehicle.");
    const res = sys.returnVehicle(num, actualDays);

    const bill = document.getElementById('returnBill');
    bill.classList.remove('hidden');
    bill.innerHTML = `
      <div class="bill-row"><span>Renter:</span> <strong>${res.renter}</strong></div>
      <div class="bill-row"><span>Base Rent Cost:</span> <strong>${formatRs(res.finalRent)}</strong></div>
      ${res.penalty > 0 ? `<div class="bill-row" style="color:var(--danger)"><span>Late Penalty:</span> <strong>${formatRs(res.penalty)}</strong></div>` : ''}
      <div class="bill-total"><span>TOTAL:</span> <strong>${formatRs(res.total)}</strong></div>
    `;
    showToast('Vehicle returned successfully!');
    refreshUI();
  } catch(e) { showToast(e.message, 'error'); }
});

document.getElementById('fleetAddBtn').addEventListener('click', () => document.getElementById('nav-add').click());
document.getElementById('clearHistoryBtn').addEventListener('click', () => {
  sys.transactions = [];
  sys.saveData();
  refreshUI();
  showToast('History cleared.');
});

refreshUI();
