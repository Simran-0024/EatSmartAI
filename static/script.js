// Login
async function login() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  if (!email || !password) {
    document.getElementById('msg').textContent = 'Sab fields bharo!';
    return;
  }

  const res = await fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();
  if (data.success) {
    window.location.href = '/dashboard';
  } else {
    document.getElementById('msg').textContent = data.message;
  }
}

// Signup
async function signup() {
  const name = document.getElementById('name')?.value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  if (!name || !email || !password) {
    document.getElementById('msg').textContent = 'Sab fields bharo!';
    return;
  }

  const res = await fetch('/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password })
  });

  const data = await res.json();
  if (data.success) {
    window.location.href = data.redirect || '/dashboard';
  } else {
    document.getElementById('msg').textContent = data.message;
  }
}

// Save Health Profile
async function saveHealth() {
  const blood_glucose = document.getElementById('blood_glucose').value;
  const cholesterol = document.getElementById('cholesterol').value;

  if (!blood_glucose || !cholesterol) {
    document.getElementById('msg').textContent = 'Dono values bharo!';
    return;
  }

  const res = await fetch('/health-profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ blood_glucose, cholesterol })
  });

  const data = await res.json();
  if (data.success) {
    window.location.href = '/dashboard';
  }
}

// Preview
const fileInput = document.getElementById('fileInput');
if (fileInput) {
  fileInput.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
      const preview = document.getElementById('preview');
      preview.src = URL.createObjectURL(file);
      preview.style.display = 'block';
    }
  });
}

// Predict
async function predict() {
  const file = document.getElementById('fileInput').files[0];
  if (!file) { alert('Pehle image select karo!'); return; }

  const formData = new FormData();
  formData.append('image', file);

  document.getElementById('result').textContent = 'Identifying...';
  document.getElementById('confidence').textContent = '';
  document.getElementById('calories').textContent = '';
  document.getElementById('suggestion').textContent = '';
  document.getElementById('reasons').textContent = '';

  try {
    const res = await fetch('/predict', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    document.getElementById('result').textContent = data.prediction.replace(/_/g, ' ');
    document.getElementById('confidence').textContent = 'Confidence: ' + data.confidence + '%';
    document.getElementById('calories').textContent = 'Calories: ' + data.calories + ' kcal per 100g';
    document.getElementById('suggestion').textContent = data.suggestion;
    document.getElementById('reasons').textContent = data.reasons.join(' • ');
  } catch (err) {
    document.getElementById('result').textContent =  err.message;
  }
}