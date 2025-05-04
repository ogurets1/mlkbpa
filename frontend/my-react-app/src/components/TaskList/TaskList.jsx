import React from 'react';
import TaskCard from '../TaskCard';
import styles from './TaskList.module.css';

const TaskList = ({ tasks }) => {
  if (tasks.length === 0) {
    return (
      <div className={styles.emptyState}>
        <img src="/empty-state.svg" alt="No tasks" />
        <p>No tasks found. Upload an image to start analysis!</p>
      </div>
    );
  }

  return (
    <div className={styles.results}>
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
};

export default TaskList;