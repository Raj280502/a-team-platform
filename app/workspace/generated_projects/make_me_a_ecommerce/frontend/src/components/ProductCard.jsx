import React from 'react';

const ProductCard = ({ product, onAddToCart }) => {
  return (
    <div className="item-card" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
      {product.image && (
        <img
          src={product.image}
          alt={product.name}
          style={{ width: '100%', height: '180px', objectFit: 'cover', borderRadius: '8px', marginBottom: '12px' }}
        />
      )}
      <div className="item-title">{product.name || 'Product'}</div>
      {product.description && (
        <div className="item-description" style={{ marginTop: '4px' }}>
          {product.description}
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', marginTop: '12px' }}>
        <span style={{ fontWeight: '700', fontSize: '1.1rem', color: '#667eea' }}>
          ${product.price ? Number(product.price).toFixed(2) : '0.00'}
        </span>
        {onAddToCart && (
          <button
            className="btn btn-primary"
            style={{ fontSize: '0.8rem', padding: '6px 14px' }}
            onClick={() => onAddToCart(product)}
          >
            🛒 Add to Cart
          </button>
        )}
      </div>
    </div>
  );
};

export default ProductCard;
