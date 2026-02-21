import React from 'react';

interface MetricCardProps {
  label: string;
  value: string;
  change?: string;
  changeColor?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  change,
  changeColor = 'inherit',
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="text-sm text-gray-500 font-medium">{label}</div>
      <div className="text-2xl font-bold text-gray-900 mt-1">{value}</div>
      {change && (
        <div className="text-sm mt-1" style={{ color: changeColor }}>
          {change}
        </div>
      )}
    </div>
  );
};
