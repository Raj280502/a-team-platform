import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import AccountSettingsForm from './components/AccountSettingsForm';
import CartList from './components/CartList';
import CategoryList from './components/CategoryList';
import CheckoutButton from './components/CheckoutButton';
import OrderHistoryList from './components/OrderHistoryList';
import OrderSummary from './components/OrderSummary';
import PaymentForm from './components/PaymentForm';
import PaymentMethodList from './components/PaymentMethodList';
import ProductDescription from './components/ProductDescription';
import ProductGrid from './components/ProductGrid';
import ProductHeader from './components/ProductHeader';
import ReviewList from './components/ReviewList';
import SearchBar from './components/SearchBar';
import ShippingForm from './components/ShippingForm';

function App() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedProduct, setSelectedProduct] = useState({});
  const [cart, setCart] = useState([]);
  const [shippingInfo, setShippingInfo] = useState({
    name: '',
    email: '',
    address: '',
    city: '',
    state: '',
    zip: '',
  });
  const [paymentInfo, setPaymentInfo] = useState({
    cardNumber: '',
    expirationDate: '',
    cvv: '',
  });
  const [orderSummary, setOrderSummary] = useState({});
  const [orderHistory, setOrderHistory] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [accountSettings, setAccountSettings] = useState({
    name: '',
    email: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:5000/api/products')
      .then(response => {
        setProducts(response.data);
      })
      .catch(error => {
        setError(error.message);
      });
  }, []);

  useEffect(() => {
    axios.get('http://localhost:5000/api/categories')
      .then(response => {
        setCategories(response.data);
      })
      .catch(error => {
        setError(error.message);
      });
  }, []);

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
  };

  const handleProductSelect = (product) => {
    setSelectedProduct(product);
  };

  const handleAddToCart = (product) => {
    setCart([...cart, product]);
  };

  const handleUpdateQuantity = (product, quantity) => {
    const updatedCart = cart.map((item) => {
      if (item.id === product.id) {
        item.quantity = quantity;
      }
      return item;
    });
    setCart(updatedCart);
  };

  const handleRemoveFromCart = (product) => {
    setCart(cart.filter((item) => item.id !== product.id));
  };

  const handleCheckout = () => {
    setLoading(true);
    axios.post('http://localhost:5000/api/orders', {
      shippingInfo,
      paymentInfo,
      cart,
    })
      .then(response => {
        setOrderSummary(response.data);
        setSuccess('Order placed successfully!');
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  };

  const handleShippingInfoChange = (event) => {
    setShippingInfo({
      ...shippingInfo,
      [event.target.name]: event.target.value,
    });
  };

  const handlePaymentInfoChange = (event) => {
    setPaymentInfo({
      ...paymentInfo,
      [event.target.name]: event.target.value,
    });
  };

  const handleAccountSettingsChange = (event) => {
    setAccountSettings({
      ...accountSettings,
      [event.target.name]: event.target.value,
    });
  };

  const handleSaveAccountSettings = () => {
    axios.put('http://localhost:5000/api/users', accountSettings)
      .then(response => {
        setSuccess('Account settings saved successfully!');
      })
      .catch(error => {
        setError(error.message);
      });
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1 className="header-title">E-Commerce Website</h1>
        <SearchBar
          searchTerm={searchTerm}
          handleSearch={handleSearch}
        />
      </header>
      <main className="main">
        <CategoryList
          categories={categories}
          handleCategorySelect={handleCategorySelect}
        />
        <ProductGrid
          products={products}
          handleProductSelect={handleProductSelect}
          handleAddToCart={handleAddToCart}
        />
        <ProductHeader
          product={selectedProduct}
        />
        <ProductDescription
          product={selectedProduct}
        />
        <ReviewList
          product={selectedProduct}
        />
        <CartList
          cart={cart}
          handleUpdateQuantity={handleUpdateQuantity}
          handleRemoveFromCart={handleRemoveFromCart}
        />
        <CheckoutButton
          handleCheckout={handleCheckout}
        />
        <ShippingForm
          shippingInfo={shippingInfo}
          handleShippingInfoChange={handleShippingInfoChange}
        />
        <PaymentForm
          paymentInfo={paymentInfo}
          handlePaymentInfoChange={handlePaymentInfoChange}
        />
        <OrderSummary
          orderSummary={orderSummary}
        />
        <OrderHistoryList
          orderHistory={orderHistory}
        />
        <PaymentMethodList
          paymentMethods={paymentMethods}
        />
        <AccountSettingsForm
          accountSettings={accountSettings}
          handleAccountSettingsChange={handleAccountSettingsChange}
          handleSaveAccountSettings={handleSaveAccountSettings}
        />
      </main>
      {loading && <div className="loading-overlay">Loading...</div>}
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
    </div>
  );
}

export default App;