import React from 'react';
import { motion } from 'framer-motion';
import './SkeletonLoader.css';

export interface SkeletonLoaderProps {
  variant?: 'card' | 'text' | 'circle' | 'rectangle';
  width?: string | number;
  height?: string | number;
  count?: number;
  className?: string;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  variant = 'rectangle',
  width = '100%',
  height = '20px',
  count = 1,
  className = ''
}) => {
  const renderSkeleton = () => {
    const style = {
      width: typeof width === 'number' ? `${width}px` : width,
      height: typeof height === 'number' ? `${height}px` : height
    };

    const skeletonElement = (
      <motion.div
        className={`skeleton-loader skeleton-loader--${variant}`}
        style={style}
        animate={{
          opacity: [0.5, 0.8, 0.5]
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      />
    );

    return skeletonElement;
  };

  if (count === 1) {
    return <div className={className}>{renderSkeleton()}</div>;
  }

  return (
    <div className={`skeleton-loader-group ${className}`}>
      {Array.from({ length: count }).map((_, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: index * 0.1 }}
        >
          {renderSkeleton()}
        </motion.div>
      ))}
    </div>
  );
};

export const SkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`skeleton-card ${className}`}>
      <div className="skeleton-card__header">
        <SkeletonLoader variant="text" height="24px" width="70%" />
        <SkeletonLoader variant="text" height="16px" width="40%" />
      </div>
      <div className="skeleton-card__body">
        <SkeletonLoader variant="text" height="16px" count={3} />
      </div>
      <div className="skeleton-card__footer">
        <SkeletonLoader variant="rectangle" height="36px" width="120px" />
      </div>
    </div>
  );
};

export const SkeletonFeedList: React.FC<{ count?: number; className?: string }> = ({ 
  count = 3,
  className = '' 
}) => {
  return (
    <div className={`skeleton-feed-list ${className}`}>
      {Array.from({ length: count }).map((_, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <SkeletonCard />
        </motion.div>
      ))}
    </div>
  );
};

export default SkeletonLoader;
