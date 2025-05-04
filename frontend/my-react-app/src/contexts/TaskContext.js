// frontend/src/contexts/TaskContext.js
import React, { createContext, useContext, useState, useCallback } from 'react';
import { getTask } from '../services/api';

const TaskContext = createContext();

export const TaskProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Добавление новой задачи
  const addTask = useCallback((newTask) => {
    setTasks(prev => [newTask, ...prev]);
  }, []);

  // Обновление существующей задачи
  const updateTask = useCallback((updatedTask) => {
    setTasks(prev => prev.map(task => 
      task.id === updatedTask.id ? updatedTask : task
    ));
  }, []);

  // Получение статуса задачи с интервалом
  const pollTaskStatus = useCallback(async (taskId) => {
    try {
      setLoading(true);
      const { data } = await getTask(taskId);
      updateTask(data);
      
      if (data.status !== 'completed') {
        setTimeout(() => pollTaskStatus(taskId), 2000);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [updateTask]);

  // Значение контекста
  const value = {
    tasks,
    loading,
    error,
    addTask,
    updateTask,
    pollTaskStatus
  };

  return (
    <TaskContext.Provider value={value}>
      {children}
    </TaskContext.Provider>
  );
};

// Хук для использования контекста
export const useTasks = () => {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error('useTasks must be used within a TaskProvider');
  }
  return context;
};