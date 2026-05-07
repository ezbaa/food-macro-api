<template>
  <div class="container">
    <div v-if="!user">
      <p>Loading...</p>
    </div>

    <div v-else>
      <header>
        <h1>Food Macro API</h1>
        <div class="user-info">
          <p>Hello, {{ user }}</p>
          <button class="logout-btn" @click="logout">Logout</button>
        </div>
      </header>

      <main>
        <div class="upload-section">
          <h2 class="upload-title">Analyze your meal</h2>

          <p class="upload-description">
            Upload a photo of your meal and get an instant macro estimate.
          </p>

          <input type="file" @change="onFileSelect" accept="image/*" />
          <p v-if="error" class="error">{{ error }}</p>

          <div v-if="loading" class="scanner-overlay">
            <div class="scanner-box">
              <div class="scan-line"></div>
              <p class="scanner-text">Calculating macros...</p>
            </div>
          </div>

          <button class="analyze-btn" @click="analyzeImage" :disabled="loading">
            {{ loading ? "Analyzing..." : "Analyze" }}
          </button>
        </div>

        <div v-if="result">
          <div v-if="result.analysis.success" class="result">
            <div class="info-card">
              <h2>{{ result.analysis.data.title }}</h2>
              <p class="summary">{{ result.analysis.data.summary }}</p>
              <div class="badges">
                <span class="badge">{{ result.analysis.data.dish_type }}</span>
                <span class="badge"
                  >{{ result.analysis.data.confidence * 100 }}% confidence</span
                >
              </div>
            </div>

            <div class="info-card">
              <h3>Ingredients</h3>
              <div class="ingredient-list">
                <span
                  class="ingredient"
                  v-for="ingredient in result.analysis.data.ingredients"
                  :key="ingredient"
                >
                  {{ ingredient }}
                </span>
              </div>
            </div>

            <div class="info-card">
              <h3>Macros</h3>
              <div class="macros">
                <div class="macro">
                  <span class="macro-value">{{
                    result.analysis.data.estimated_macros.calories
                  }}</span>
                  <span class="macro-label">kcal</span>
                </div>
                <div class="macro">
                  <span class="macro-value"
                    >{{
                      result.analysis.data.estimated_macros.protein_g
                    }}g</span
                  >
                  <span class="macro-label">Protein</span>
                </div>
                <div class="macro">
                  <span class="macro-value"
                    >{{ result.analysis.data.estimated_macros.carbs_g }}g</span
                  >
                  <span class="macro-label">Carbs</span>
                </div>
                <div class="macro">
                  <span class="macro-value"
                    >{{ result.analysis.data.estimated_macros.fat_g }}g</span
                  >
                  <span class="macro-label">Fat</span>
                </div>
                <div class="macro">
                  <span class="macro-value"
                    >{{ result.analysis.data.estimated_macros.sugar_g }}g</span
                  >
                  <span class="macro-label">Sugar</span>
                </div>
                <div class="macro">
                  <span class="macro-value"
                    >{{ result.analysis.data.estimated_macros.fiber_g }}g</span
                  >
                  <span class="macro-label">Fiber</span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="error-card">
            <p>{{ result.analysis.error }}</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const user = ref(null);
const file = ref(null);
const result = ref(null);
const loading = ref(false);
const error = ref(null);

onMounted(async () => {
  try {
    const response = await fetch("http://localhost:8080/me", {
      credentials: "include",
    });
    if (!response.ok) {
      router.push("/");
      return;
    }
    const data = await response.json();
    user.value = data.username;
  } catch {
    router.push("/");
  }
});

function onFileSelect(event) {
  file.value = event.target.files[0];
}

async function analyzeImage() {
  if (!file.value) {
    error.value = "Upload image";
    return;
  }

  result.value = null;

  loading.value = true;
  error.value = null;
  try {
    const formData = new FormData();
    formData.append("file", file.value);

    const response = await fetch("http://localhost:8080/analyze-image", {
      method: "POST",
      credentials: "include",
      body: formData,
    });

    if (!response.ok) {
      const data = await response.json();
      error.value = data.detail;
      return;
    }
    const data = await response.json();
    console.log(data);
    result.value = data;
  } catch {
    error.value = "Something went wrong";
  } finally {
    loading.value = false;
  }
}

async function logout() {
  await fetch("http://localhost:8080/logout", {
    method: "POST",
    credentials: "include",
  });
  router.push("/");
}
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.container {
  background-color: #f4f7f2;
  min-height: 100vh;
  color: #1f2a1f;
  font-family:
    system-ui,
    -apple-system,
    sans-serif;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 48px;
  border-bottom: 1px solid #dce5da;
  background: #f4f7f2;
}

header h1 {
  font-size: 1.3rem;
  color: #1f2a1f;
}

main {
  max-width: 680px;
  margin: 0 auto;
  padding: 40px 24px;
}

.upload-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2f3b2f;
  margin-bottom: 4px;
}

.upload-section {
  position: relative;
  background: #ffffff;
  border: 1px solid #dce5da;
  border-radius: 18px;
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  margin-bottom: 40px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.04);
}

.upload-description {
  color: #5c6b5c;
  font-size: 0.95rem;
  text-align: center;
  max-width: 420px;
  line-height: 1.5;
}

input[type="file"] {
  background: #f7faf5;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid #dce5da;
  color: #2f3b2f;
  width: 100%;
  max-width: 400px;
  position: relative;
  overflow: hidden;
}

.analyze-btn {
  padding: 12px 28px;
  background-color: #6ba368;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  cursor: pointer;
  width: 100%;
  max-width: 400px;
  transition: all 0.2s ease;
}

.analyze-btn:hover {
  background-color: #5b8f58;
  transform: translateY(-1px);
}

.analyze-btn:disabled {
  background-color: #b8c7b6;
  cursor: not-allowed;
}
.error-card {
  background: #fff7ed;
  border: 1px solid #fcd9a8;
  border-radius: 12px;
  padding: 20px;
  color: #b45309;
}

.error {
  color: #b45309;
  font-size: 0.9rem;
}

.info-card {
  background: #ffffff;
  border: 1px solid #dce5da;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
}

.info-card h2 {
  font-size: 1.4rem;
  margin-bottom: 8px;
}

.info-card h3 {
  font-size: 0.8rem;
  margin-bottom: 16px;
  color: #7a8a7a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary {
  color: #5c6b5c;
  margin-bottom: 16px;
  line-height: 1.5;
}

.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.badge {
  background-color: #eaf3ea;
  color: #5b8f58;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  border: 1px solid #dce5da;
}

.ingredient {
  background-color: #f3f7f2;
  color: #2f3b2f;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  border: 1px solid #dce5da;
  margin: 2px;
}

.ingredient-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.macros {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.macro {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background-color: #f3f7f2;
  border-radius: 10px;
  border: 1px solid #dce5da;
}

.macro-value {
  font-size: 1.4rem;
  font-weight: bold;
  color: #6ba368;
}

.macro-label {
  color: #7a8a7a;
  font-size: 0.8rem;
  margin-top: 4px;
}

.macro {
  transition: transform 0.15s ease;
}

.macro:hover {
  transform: scale(1.03);
  border-color: #bfd6bb;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #5c6b5c;
  font-size: 0.9rem;
}

.logout-btn {
  padding: 6px 14px;
  background: transparent;
  color: #5c6b5c;
  border: 1px solid #c9d6c6;
  border-radius: 8px;
  cursor: pointer;
}

.logout-btn:hover {
  background: #e6eee3;
  color: #1f2a1f;
}

.scanner-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  z-index: 10;
}

.scanner-box {
  position: relative;
  width: 220px;
  height: 220px;
  border-radius: 16px;
  background: linear-gradient(145deg, #f3f8f2, #e4efe6);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 20px;
  overflow: hidden;
}

.scan-line {
  position: absolute;
  top: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(to right, transparent, #6baa75, transparent);
  animation: scanMove 2s ease-in-out infinite;
}

.scanner-text {
  font-weight: 600;
  color: #4f6f52;
  letter-spacing: 0.5px;
  animation: pulse 1.8s ease-in-out infinite;
}

.info-card,
.upload-section {
  transition:
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.06);
}

@keyframes scanMove {
  0% {
    top: 0;
  }
  50% {
    top: calc(100% - 4px);
  }
  100% {
    top: 0;
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

.loading-text {
  text-align: center;
  color: #6ba368;
  font-weight: 500;
  margin-bottom: 16px;
}
</style>
