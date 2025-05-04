import { useState } from 'react';
import UploadForm from './components/UploadForm';
import TaskList from './components/TaskList';
import { uploadFile, getTask } from './services/api';
import useTaskPolling from './hooks/useTaskPolling';
import styles from './App.module.css';

const App = () => {
  const [tasks, setTasks] = useState([]);
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  
  const task = useTaskPolling(currentTaskId);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!isUploading) {
      try {
        setIsUploading(true);
        const { data } = await uploadFile(e.target.file.files[0]);
        setCurrentTaskId(data.id);
      } catch (error) {
        console.error('Upload failed:', error);
      } finally {
        setIsUploading(false);
      }
    }
  };

  useEffect(() => {
    if (task) {
      setTasks(prev => [task, ...prev]);
    }
  }, [task]);

  return (
    <div className={styles.container}>
      <h1>Object Detection App</h1>
      <UploadForm 
        onFileSelect={(e) => e.target.files[0] && setFile(e.target.files[0])}
        onSubmit={handleUpload}
        isUploading={isUploading}
      />
      <TaskList tasks={tasks} />
    </div>
  );
};

export default App;