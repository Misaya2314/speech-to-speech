import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import SimpleCounter from '@/components/SimpleCounter.vue';

describe('SimpleCounter.vue', () => {
  it('正确渲染初始状态', () => {
    const wrapper = mount(SimpleCounter, {
      props: {
        title: '测试计数器',
        initialValue: 5
      }
    });
    
    // 验证标题和初始计数值
    expect(wrapper.find('h3').text()).toBe('测试计数器');
    expect(wrapper.find('.counter-display').text()).toBe('5');
    
    // 检查按钮状态
    const decrementBtn = wrapper.find('.decrement');
    const incrementBtn = wrapper.find('.increment');
    expect(decrementBtn.attributes('disabled')).toBeFalsy();
    expect(incrementBtn.attributes('disabled')).toBeFalsy();
  });
  
  it('点击增加按钮应该增加计数值', async () => {
    const wrapper = mount(SimpleCounter, {
      props: {
        initialValue: 1
      }
    });
    
    await wrapper.find('.increment').trigger('click');
    expect(wrapper.find('.counter-display').text()).toBe('2');
    
    // 验证是否发出了change事件
    expect(wrapper.emitted()).toHaveProperty('change');
    expect(wrapper.emitted().change[0]).toEqual([2]);
  });
  
  it('点击减少按钮应该减少计数值', async () => {
    const wrapper = mount(SimpleCounter, {
      props: {
        initialValue: 3
      }
    });
    
    await wrapper.find('.decrement').trigger('click');
    expect(wrapper.find('.counter-display').text()).toBe('2');
    
    // 验证是否发出了change事件
    expect(wrapper.emitted()).toHaveProperty('change');
    expect(wrapper.emitted().change[0]).toEqual([2]);
  });
  
  it('计数值为0时减少按钮应该被禁用', async () => {
    const wrapper = mount(SimpleCounter);
    
    // 初始值为0，减少按钮应该被禁用
    expect(wrapper.find('.counter-display').text()).toBe('0');
    expect(wrapper.find('.decrement').attributes('disabled')).toBeDefined();
    
    // 点击增加按钮后，减少按钮应该变为可用
    await wrapper.find('.increment').trigger('click');
    expect(wrapper.find('.counter-display').text()).toBe('1');
    expect(wrapper.find('.decrement').attributes('disabled')).toBeFalsy();
  });
  
  it('点击重置按钮应该将计数重置为初始值', async () => {
    const wrapper = mount(SimpleCounter, {
      props: {
        initialValue: 10
      }
    });
    
    // 改变计数值
    await wrapper.find('.decrement').trigger('click');
    await wrapper.find('.decrement').trigger('click');
    expect(wrapper.find('.counter-display').text()).toBe('8');
    
    // 点击重置按钮
    await wrapper.find('[data-testid="reset-button"]').trigger('click');
    expect(wrapper.find('.counter-display').text()).toBe('10');
    
    // 验证是否发出了reset事件
    expect(wrapper.emitted()).toHaveProperty('reset');
    expect(wrapper.emitted().reset[0]).toEqual([10]);
  });
}); 