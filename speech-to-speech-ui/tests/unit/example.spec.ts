import { describe, it, expect } from 'vitest';

// 一个简单的函数用于测试
function sum(a: number, b: number): number {
  return a + b;
}

describe('基础测试示例', () => {
  it('1 + 1 等于 2', () => {
    expect(1 + 1).toBe(2);
  });

  it('sum函数应该正确计算两个数的和', () => {
    expect(sum(1, 2)).toBe(3);
    expect(sum(-1, 1)).toBe(0);
    expect(sum(5, 5)).toBe(10);
  });
  
  it('数组测试', () => {
    const arr = [1, 2, 3];
    expect(arr).toHaveLength(3);
    expect(arr).toContain(2);
    expect(arr).not.toContain(4);
  });
  
  it('对象测试', () => {
    const obj = { name: '测试', value: 42 };
    expect(obj).toHaveProperty('name');
    expect(obj.name).toBe('测试');
    expect(obj.value).toBe(42);
  });
}); 