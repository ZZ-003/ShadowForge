'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/lib/store/auth';
import { getTasks, TaskStatus } from '@/lib/api/tasks';
import { getUserFiles, getDownloadUrl } from '@/lib/api/files';
import type { Task } from '@/lib/api/tasks';
import type { FileInfo } from '@/lib/api/files';

// 下载文件的辅助函数
const downloadFile = async (filePath: string) => {
  try {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('auth_token');
    
    const response = await fetch(getDownloadUrl(filePath), {
      method: 'GET',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
      },
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        alert('请先登录');
        window.location.href = '/auth/login';
        return;
      }
      throw new Error(`下载失败：${response.status}`);
    }
    
    // 获取文件 blob
    const blob = await response.blob();
    
    // 从 Content-Disposition 或 URL 中提取文件名
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'download';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    } else {
      // 从文件路径提取文件名
      const pathParts = filePath.split(/[\\/]/);
      filename = pathParts[pathParts.length - 1];
    }
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error: any) {
    console.error('Download error:', error);
    alert(`下载失败：${error.message}`);
  }
};

export default function OutputsPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/auth/login';
      return;
    }

    const loadOutputs = async () => {
      try {
        setLoading(true);
        // 获取已完成的任务
        const allTasks = await getTasks({ status: TaskStatus.COMPLETED });
        setTasks(allTasks);
        setError(null);
      } catch (err) {
        console.error('Failed to load outputs:', err);
        setError('Failed to load output files');
      } finally {
        setLoading(false);
      }
    };

    loadOutputs();
  }, [isAuthenticated]);

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    switch (ext) {
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
      case 'bmp':
        return '🖼️';
      case 'mp4':
      case 'avi':
      case 'mov':
        return '🎥';
      case 'mp3':
      case 'wav':
      case 'ogg':
        return '🎵';
      case 'pdf':
        return '📄';
      case 'doc':
      case 'docx':
        return '📝';
      case 'ppt':
      case 'pptx':
        return '📊';
      default:
        return '📁';
    }
  };

  if (loading) {
    return (
      <div className="cyber-card text-center py-12">
        <div className="animate-pulse">正在加载输出文件...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="cyber-card text-center py-12">
        <div className="text-red-400 mb-4">{error}</div>
        <button
          onClick={() => window.location.reload()}
          className="cyber-button"
        >
          重试
        </button>
      </div>
    );
  }

  // Filter tasks that have output files
  const tasksWithOutputs = tasks.filter(task => task.output_files && task.output_files.length > 0);

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <h1 className="text-2xl font-bold text-gradient">输出文件</h1>
        <Link href="/dashboard/tasks" className="cyber-button">
          查看全部任务
        </Link>
      </motion.div>

      {tasksWithOutputs.length === 0 ? (
        <div className="cyber-card text-center py-12">
          <div className="text-gray-400 mb-4">暂无输出文件</div>
          <Link href="/dashboard/tasks/new" className="cyber-button">
            创建新任务
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tasksWithOutputs.map((task) => (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="cyber-card p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-cyber-blue/20 rounded-lg flex items-center justify-center">
                  <span className="text-xl">⚡</span>
                </div>
                <div>
                  <h3 className="font-semibold text-white">{task.name}</h3>
                  <p className="text-sm text-gray-400">Task #{task.id}</p>
                </div>
              </div>
              
              <div className="space-y-3">
                {task.output_files?.map((file, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-cyber-dark/50 rounded-lg">
                    <span className="text-2xl">{getFileIcon(file)}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{file}</p>
                      <p className="text-xs text-gray-400">
                        Generated: {new Date(task.completed_at || task.created_at).toLocaleString()}
                      </p>
                    </div>
                    <button
                      onClick={() => downloadFile(file)}
                      className="cyber-button text-xs px-3 py-1"
                    >
                      下载
                    </button>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}