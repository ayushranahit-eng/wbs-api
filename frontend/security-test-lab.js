const previewResult = document.getElementById('previewResult');
const previewInput = document.getElementById('previewInput');
const redirectInput = document.getElementById('redirectInput');
const redirectStatus = document.getElementById('redirectStatus');
const storedResult = document.getElementById('storedResult');
const commentForm = document.getElementById('commentForm');

const demoSecrets = {
  awsAccessKey: 'AKIAIOSFODNN7EXAMPLE',
  githubToken: 'ghp_1234567890abcdefghijklmnopqrstuv',
  stripeLikeKey: 'sk_live_demo_public_training_value_123456789',
  internalApiBase: 'https://wbs-api-production-4d02.up.railway.app/internal'
};

function params() {
  return new URLSearchParams(window.location.search);
}

function renderPreview(value) {
  previewResult.innerHTML = value || 'No preview set';
}

function renderStoredComment() {
  const saved = localStorage.getItem('wbs-security-lab-comment') || 'No saved comment yet';
  storedResult.innerHTML = saved;
}

function unsafeRedirect(target) {
  redirectStatus.textContent = 'Current target: ' + (target || 'none');
  if (target) {
    window.location.href = target;
  }
}

previewInput.value = params().get('preview') || window.location.hash.slice(1) || '';
redirectInput.value = params().get('next') || '';
redirectStatus.textContent = 'Current target: ' + (redirectInput.value || 'none');
renderPreview(previewInput.value);
renderStoredComment();

if (params().get('autoroute') === '1') {
  unsafeRedirect(redirectInput.value);
}

document.getElementById('previewBtn').addEventListener('click', () => {
  renderPreview(previewInput.value);
});

document.getElementById('redirectBtn').addEventListener('click', () => {
  unsafeRedirect(redirectInput.value);
});

commentForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const saved = document.getElementById('commentInput').value;
  localStorage.setItem('wbs-security-lab-comment', saved);
  renderStoredComment();
});

window.demoSecrets = demoSecrets;

//# sourceMappingURL=security-test-lab.js.map
