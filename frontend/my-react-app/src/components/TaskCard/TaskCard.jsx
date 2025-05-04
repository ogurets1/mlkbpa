import React from 'react';
import PropTypes from 'prop-types';
import styles from './TaskCard.module.css';

const TaskCard = ({ task }) => {
  const handleImageError = (e) => {
    e.target.src = '/image-placeholder.svg';
  };

  return (
    <div className={styles.card}>
      <img 
        src={task.result_url || '/image-placeholder.svg'} 
        alt="Detection result" 
        className={styles.image}
        onError={handleImageError}
      />
      <div className={styles.detections}>
        {task.detections?.length > 0 ? (
          task.detections.map((d, i) => (
            <div key={`${d.class}-${i}`} className={styles.detection}>
              <span className={styles.className}>{d.class}</span>
              <span className={styles.confidence}>
                {(d.confidence * 100).toFixed(1)}%
              </span>
            </div>
          ))
        ) : (
          <div className={styles.noDetections}>No objects detected</div>
        )}
      </div>
    </div>
  );
};

TaskCard.propTypes = {
  task: PropTypes.shape({
    id: PropTypes.string.isRequired,
    result_url: PropTypes.string,
    detections: PropTypes.arrayOf(
      PropTypes.shape({
        class: PropTypes.string,
        confidence: PropTypes.number
      })
    )
  }).isRequired
};

export default TaskCard;