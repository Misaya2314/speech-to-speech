<template>
  <div class="counter-container">
    <h3>{{ title }}</h3>
    <div class="counter-display">{{ count }}</div>
    <div class="counter-controls">
      <button class="counter-button decrement" @click="decrement" :disabled="count <= 0">-</button>
      <button class="counter-button increment" @click="increment">+</button>
    </div>
    <button class="reset-button" @click="reset" data-testid="reset-button">重置</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps({
  title: {
    type: String,
    default: '计数器'
  },
  initialValue: {
    type: Number,
    default: 0
  }
});

const count = ref(props.initialValue);

const increment = () => {
  count.value++;
  emit('change', count.value);
};

const decrement = () => {
  if (count.value > 0) {
    count.value--;
    emit('change', count.value);
  }
};

const reset = () => {
  count.value = props.initialValue;
  emit('reset', count.value);
};

const emit = defineEmits(['change', 'reset']);
</script>

<style scoped>
.counter-container {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  width: 200px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.counter-display {
  font-size: 2rem;
  font-weight: bold;
  margin: 16px 0;
}

.counter-controls {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
}

.counter-button {
  width: 40px;
  height: 40px;
  font-size: 1.5rem;
  border: none;
  border-radius: 50%;
  cursor: pointer;
}

.increment {
  background-color: #4caf50;
  color: white;
}

.decrement {
  background-color: #f44336;
  color: white;
}

.decrement:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.reset-button {
  padding: 8px 16px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style> 