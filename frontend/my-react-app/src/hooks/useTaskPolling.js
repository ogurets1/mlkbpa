import { useState, useEffect } from 'react';
import { getTask } from '../services/api';

const useTaskPolling = (taskId) => {
  const [task, setTask] = useState(null);

  useEffect(() => {
    let isMounted = true;
    
    const poll = async () => {
      try {
        const result = await getTask(taskId);
        if (isMounted) {
          setTask(result);
          if (result.status !== 'completed') {
            setTimeout(poll, 2000);
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    if (taskId) poll();

    return () => {
      isMounted = false;
    };
  }, [taskId]);

  return task;
};

export default useTaskPolling;