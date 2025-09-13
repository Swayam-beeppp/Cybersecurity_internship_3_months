import React from 'react';

const Card = ({ title, children }) => {
  return (
    <div className="bg-gray-800 text-white p-4 rounded-xl shadow-md border border-gray-700">
      {title && <h3 className="text-xl font-bold mb-2">{title}</h3>}
      <div>{children}</div>
    </div>
  );
};

export default Card;
