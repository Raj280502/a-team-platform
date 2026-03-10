import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ProductHeader.css';

const ProductHeader = (props) => {
  const [product, setProduct] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/products/${props.productId}`);
        setProduct(response.data);
        setLoading(false);
      } catch (error) {
        setError(error.message);
        setLoading(false);
      }
    };
    fetchProduct();
  }, [props.productId]);

  if (loading) {
    return <div className="product-header-loading">Loading...</div>;
  }

  if (error) {
    return <div className="product-header-error">Error: {error}</div>;
  }

  return (
    <div className="product-header">
      <h1 className="product-header-title">{product.name}</h1>
      <p className="product-header-description">{product.description}</p>
      <div className="product-header-price">${product.price}</div>
      <button className="product-header-button" onClick={() => props.handleAddToCart(product.id)}>Add to Cart</button>
    </div>
  );
};

export default ProductHeader;