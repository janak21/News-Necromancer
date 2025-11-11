import React from 'react';
import SpookySpinner from '../SpookySpinner';
import { SkeletonFeedList } from '../SkeletonLoader';
import './LoadingState.css';

export type LoadingOperation = 
  | 'feed-processing'
  | 'image-generation'
  | 'story-continuation'
  | 'export'
  | 'preferences'
  | 'authentication'
  | 'generic';

export interface LoadingStateProps {
  operation?: LoadingOperation;
  message?: string;
  showSkeleton?: boolean;
  skeletonCount?: number;
  variant?: 'ghost' | 'skull' | 'spiral';
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

const operationMessages: Record<LoadingOperation, string> = {
  'feed-processing': 'Summoning dark forces...',
  'image-generation': 'Conjuring nightmares...',
  'story-continuation': 'Extending the horror...',
  'export': 'Preparing your terrors...',
  'preferences': 'Adjusting the darkness...',
  'authentication': 'Awakening the spirits...',
  'generic': 'Loading...'
};

const LoadingState: React.FC<LoadingStateProps> = ({
  operation = 'generic',
  message,
  showSkeleton = false,
  skeletonCount = 3,
  variant = 'ghost',
  size = 'medium',
  className = ''
}) => {
  const displayMessage = message || operationMessages[operation];

  if (showSkeleton) {
    return (
      <div className={`loading-state loading-state--skeleton ${className}`}>
        <SkeletonFeedList count={skeletonCount} />
      </div>
    );
  }

  return (
    <div className={`loading-state ${className}`}>
      <SpookySpinner
        message={displayMessage}
        variant={variant}
        size={size}
      />
    </div>
  );
};

export default LoadingState;
