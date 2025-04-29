import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/vue';
import * as matchers from '@testing-library/jest-dom/matchers';

// 扩展Vitest的断言
expect.extend(matchers);

// 每个测试之后自动清理
afterEach(() => {
  cleanup();
}); 