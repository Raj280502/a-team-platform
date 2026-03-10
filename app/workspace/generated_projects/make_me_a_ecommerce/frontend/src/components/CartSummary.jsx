import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CartSummary.css';

const CartSummary = ({ cartItems, handleRemoveItem, handleUpdateQuantity }) => {
  const [subtotal, setSubtotal] = useState(0);
  const [tax, setTax] = useState(0);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    let subtotalAmount = 0;
    cartItems.forEach(item => {
      subtotalAmount += item.price * item.quantity;
    });
    setSubtotal(subtotalAmount);
    setTax(subtotalAmount * 0.08);
    setTotal(subtotalAmount + (subtotalAmount * 0.08));
  }, [cartItems]);

  const handleRemove = async (itemId) => {
    try {
      await axios.delete(`http://localhost:5000/api/orders/${itemId}`);
      handleRemoveItem(itemId);
    } catch (error) {
      console.error(error);
    }
  };

  const handleQuantityUpdate = async (itemId, newQuantity) => {
    try {
      await axios.patch(`http://localhost:5000/api/orders/${itemId}`, { quantity: newQuantity });
      handleUpdateQuantity(itemId, newQuantity);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="cart-summary">
      <h2>Cart Summary</h2>
      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>Quantity</th>
            <th>Price</th>
            <th>Total</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {cartItems.map(item => (
            <tr key={item.id}>
              <td>{item.name}</td>
              <td>
                <input
                  type="number"
                  value={item.quantity}
                  onChange={(e) => handleQuantityUpdate(item.id, parseInt(e.target.value))}
                  min="1"
                />
              </td>
              <td>${item.price.toFixed(2)}</td>
              <td>${(item.price * item.quantity).toFixed(2)}</td>
              <td>
                <button onClick={() => handleRemove(item.id)}>Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="summary">
        <p>Subtotal: ${subtotal.toFixed(2)}</p>
        <p>Tax (8%): ${tax.toFixed(2)}</p>
        <p>Total: ${total.toFixed(2)}</p>
      </div>
    </div>
  );
};

export default CartSummary;