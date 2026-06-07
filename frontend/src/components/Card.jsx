import React from 'react';
import './Card.css';

const Card = ({ children, className = '', hoverable = false, ...props }) => {
  const cn = `card ${hoverable ? 'card-hoverable' : ''} ${className}`;
  return (
    <div className={cn} {...props}>
      {children}
    </div>
  );
};

export default Card;
