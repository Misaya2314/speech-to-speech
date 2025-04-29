import { describe, it, expect, vi } from 'vitest';
import { formatDate, truncateText, filterItems, delay, getRandomColor } from '@/utils/test-utils';

describe('formatDate', () => {
  it('应该格式化日期为正确的格式', () => {
    const date = new Date(2023, 0, 15, 10, 30, 45); // 2023-01-15 10:30:45
    expect(formatDate(date)).toBe('2023-01-15 10:30:45');
  });

  it('应该为月份、日期和时间补零', () => {
    const date = new Date(2023, 8, 5, 9, 5, 7); // 2023-09-05 09:05:07
    expect(formatDate(date)).toBe('2023-09-05 09:05:07');
  });
});

describe('truncateText', () => {
  it('长度小于或等于最大长度时应该返回原文本', () => {
    expect(truncateText('Hello', 5)).toBe('Hello');
    expect(truncateText('Hello', 10)).toBe('Hello');
  });

  it('长度大于最大长度时应该截断并添加省略号', () => {
    expect(truncateText('Hello World', 5)).toBe('Hello...');
    expect(truncateText('这是一个很长的文本', 4)).toBe('这是一个...');
  });
});

describe('filterItems', () => {
  it('应该正确过滤数组项目', () => {
    const numbers = [1, 2, 3, 4, 5];
    const evenNumbers = filterItems(numbers, n => n % 2 === 0);
    expect(evenNumbers).toEqual([2, 4]);
    
    const words = ['apple', 'banana', 'orange', 'pear'];
    const longWords = filterItems(words, word => word.length > 5);
    expect(longWords).toEqual(['banana', 'orange']);
  });
});

describe('delay', () => {
  it('应该在指定的时间后解析Promise', async () => {
    vi.useFakeTimers();
    
    const promise = delay(1000);
    let resolved = false;
    
    promise.then(() => {
      resolved = true;
    });
    
    expect(resolved).toBe(false);
    
    vi.advanceTimersByTime(500);
    await Promise.resolve(); // 让Promise有机会解析
    expect(resolved).toBe(false);
    
    vi.advanceTimersByTime(500);
    await Promise.resolve(); // 让Promise有机会解析
    expect(resolved).toBe(true);
    
    vi.useRealTimers();
  });
});

describe('getRandomColor', () => {
  it('应该返回一个有效的十六进制颜色代码', () => {
    const color = getRandomColor();
    expect(color).toMatch(/^#[0-9A-F]{6}$/);
  });
  
  it('应该返回不同的颜色（概率测试）', () => {
    // 由于函数是随机的，所以我们多次调用并检查是否至少有一些不同的值
    const colors = new Set();
    for (let i = 0; i < 10; i++) {
      colors.add(getRandomColor());
    }
    
    // 至少应该有多个不同的值（除非我们非常不幸）
    expect(colors.size).toBeGreaterThan(1);
  });
}); 