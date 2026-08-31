<template>
  <div>
    <h2>Your Orders</h2>
    <div v-if="orders.length===0">No orders found.</div>
    <ul>
      <li v-for="o in orders" :key="o.id">
        <div>Order #{{ o.id }} — €{{ (o.amount_cents/100).toFixed(2) }} — {{ o.fulfilled ? 'Fulfilled' : 'Pending' }} <span v-if="o.refunded">(Refunded)</span></div>
        <div v-if="o.invoice_url"><a :href="o.invoice_url" target="_blank">Download invoice</a></div>
      </li>
    </ul>
  </div>
</template>

<script>
import API from '../auth'
export default {
  name: 'CustomerOrders',
  data() {
    return { orders: [] }
  },
  async created() {
    try {
      const res = await API.get('/api/orders/my/')
      this.orders = res.data
    } catch (e) {
      console.error(e)
    }
  }
}
</script>
