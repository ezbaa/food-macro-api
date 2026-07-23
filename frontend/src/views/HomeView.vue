<template>
  <div class="container">
    <div class="card">
      <h1>Food Macro API</h1>

      <p class="subtitle">Analyze your meal and get instant nutritional insights powered by AI.</p>

      <div class="divider"></div>

      <p class="hint">Sign in with GitHub to start analyzing your food photos.</p>

      <button class="login-btn" @click="login">Login with GitHub</button>
      <p class="whitelist">Whitelisted access</p>
    </div>
  </div>
</template>

<script setup>
function login() {
  window.location.href = `${import.meta.env.VITE_API_URL}/login`
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background: #f4f7f2;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family:
    system-ui,
    -apple-system,
    sans-serif;
  color: #1f2a1f;
}

.card {
  background: #ffffff;
  border: 1px solid #dce5da;
  border-radius: 18px;
  padding: 48px 36px;
  max-width: 420px;
  text-align: center;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
  transition:
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

h1 {
  font-size: 1.8rem;
  margin-bottom: 12px;
  color: #2f3b2f;
}

.subtitle {
  color: #5c6b5c;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 24px;
}

.hint {
  color: #7a8a7a;
  font-size: 0.85rem;
  margin-bottom: 24px;
}
.whitelist {
  color: #585b58;
  font-size: 0.85rem;
  margin-bottom: 24px;
}

.divider {
  height: 1px;
  background: #dce5da;
  margin: 20px 0;
}

.login-btn {
  width: 100%;
  padding: 12px 18px;
  background-color: #2f3b2f;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.login-btn:hover {
  background-color: #3f4d3f;
  transform: translateY(-1px);
}
</style>
