import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ProductImages.css';

const ProductImages = ({ productId }) => {
  const [images, setImages] = useState([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/products/${productId}`);
        setImages(response.data.images);
      } catch (error) {
        setError(error.message);
      }
    };
    fetchImages();
  }, [productId]);

  const handleNextImage = () => {
    setActiveIndex((prevIndex) => (prevIndex + 1) % images.length);
  };

  const handlePrevImage = () => {
    setActiveIndex((prevIndex) => (prevIndex - 1 + images.length) % images.length);
  };

  if (error) {
    return <div className="error-message">Failed to load images: {error}</div>;
  }

  if (!images.length) {
    return <div className="loading-message">Loading images...</div>;
  }

  return (
    <div className="product-images">
      <div className="image-carousel">
        {images.map((image, index) => (
          <img
            key={index}
            src={image}
            alt={`Product image ${index + 1}`}
            className={index === activeIndex ? 'active' : ''}
          />
        ))}
      </div>
      <div className="carousel-controls">
        <button className="prev-button" onClick={handlePrevImage}>
          Previous
        </button>
        <button className="next-button" onClick={handleNextImage}>
          Next
        </button>
      </div>
      <div className="image-index">
        {activeIndex + 1} / {images.length}
      </div>
    </div>
  );
};

export default ProductImages;