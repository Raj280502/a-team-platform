import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProductDescription = (props) => {
  const [product, setProduct] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/products/${props.productId}`);
        setProduct(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [props.productId]);

  if (loading) {
    return <div style={{ textAlign: 'center' }}>Loading...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', color: 'red' }}>{error}</div>;
  }

  return (
    <div className="product-description">
      <h2>{product.name}</h2>
      <p>{product.description}</p>
      <ul>
        <li>Price: ${product.price}</li>
        <li>Category: {product.category}</li>
        <li>Rating: {product.rating}/5</li>
      </ul>
      <button className="btn btn-primary" onClick={() => props.addToCart(product.id)}>Add to Cart</button>
    </div>
  );
};

export default ProductDescription;