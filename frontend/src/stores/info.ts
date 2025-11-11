import { defineStore } from 'pinia';
import axios from 'axios';
import { ElMessage } from 'element-plus';

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