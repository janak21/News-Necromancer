import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './FilterResults.css';

export interface FilterResultsProps {
  totalCount: number;
  filteredCount: number;
  isFiltered: boolean;
}

const FilterResults: React.FC<FilterResultsProps> = ({
  totalCount,
  filteredCount,
  isFiltered
}) => {
  return (
    <motion.div 
      className="filter-results"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      <AnimatePresence mode="wait">
        {isFiltered ? (
          <motion.div
            key="filtered"
            className="filter-results__content"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            {filteredCount === 0 ? (
              <div className="filter-results__no-match">
                <span className="filter-results__icon">🔍</span>
                <span className="filter-results__text">
                  No matches found
                </span>
                <span className="filter-results__subtext">
                  (0 of {totalCount} variant{totalCount !== 1 ? 's' : ''})
                </span>
              </div>
            ) : (
              <div className="filter-results__match">
                <span className="filter-results__text">
                  Showing <strong className="filter-results__count">{filteredCount}</strong> of{' '}
                  <strong className="filter-results__count">{totalCount}</strong> variant{totalCount !== 1 ? 's' : ''}
                </span>
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="unfiltered"
            className="filter-results__content"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <span className="filter-results__text">
              <strong className="filter-results__count">{totalCount}</strong> variant{totalCount !== 1 ? 's' : ''} total
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default FilterResults;
