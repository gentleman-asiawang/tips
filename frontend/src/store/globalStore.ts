import { defineStore } from 'pinia';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import { ElMessage } from 'element-plus';

export const useUuidStore = defineStore('uuid', {
  state: () => ({
    uuid: '' as string,
  }),
  actions: {
    generateUuid() {
      this.uuid = uuidv4();
    },
  },
});

export const useInfoStore = defineStore('tips_info', {
  state: () => ({
    orders: [] as { orders: string; pictures: string }[],
    countall: 0,
    countspecies: 0,
    data_size: 0,
  }),
  actions: {
    async fetchOrders() {
      try {
        const response = await axios.post('/tips_api/get_orders/');
        const pictureBaseUrl = response.data.picture_url; // 存储图片URL
        this.orders = response.data.orders.map((order: string) => ({
          orders: order,
          pictures: `${pictureBaseUrl}${order}.jpg`,  // 构建图片URL
        }));
        this.countall = response.data.count_all;
        this.countspecies = response.data.count_species;
        this.data_size = response.data.data_size;
        // console.log("Fetched orders:", this.orders);
      } catch (error) {
        console.error("Error fetching categories:", error);
        ElMessage.error('Network response was not ok!');
      }
    }
  }
});

export const useTreeStore = defineStore('tree', {
  state: () => ({
    target: '',
    previousTarget: '',
    targetUUID: '', // 添加用于存储 UUID 的字段
  }),
  actions: {
    setTarget(newTarget: string) {
      if (newTarget !== this.target) {
        this.previousTarget = this.target; // 更新 previousTarget 为当前的 target 值
        this.target = newTarget; // 更新 target
        this.targetUUID = uuidv4();
      }
    },
    hasTargetChanged() {
      // 比较 current target 和 previousTarget 是否不同
      return this.target !== this.previousTarget;
    }
  }
});