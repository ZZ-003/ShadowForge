'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/lib/store/auth';
import { getTasks, TaskStatus } from '@/lib/api/tasks';
import { getUserFiles, deleteFile, type FileInfo } from '@/lib/api/files';
import type { Task } from '@/lib/api/tasks';

// 下载文件的辅助函数
const downloadFile = async (filePath: string) => {
  try {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('auth_token');
    
    const response = await fetch(`/api/files/download/${encodeURIComponent(filePath)}`, {
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
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteResult, setDeleteResult] = useState<{ success: number; failed: number; errors: string[] } | null>(null);
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
        
        // 获取所有文件
        const allFiles = await getUserFiles();
        setFiles(allFiles);
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

  // 处理单个文件选择
  const handleSelectFile = (filePath: string) => {
    const newSelected = new Set(selectedFiles);
    if (newSelected.has(filePath)) {
      newSelected.delete(filePath);
    } else {
      newSelected.add(filePath);
    }
    setSelectedFiles(newSelected);
    setDeleteResult(null);
  };

  // 全选/反选
  const handleSelectAll = () => {
    if (selectedFiles.size === files.length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(files.map(f => f.path)));
    }
    setDeleteResult(null);
  };

  // 反选
  const handleInvertSelection = () => {
    const newSelected = new Set<string>();
    files.forEach(file => {
      if (!selectedFiles.has(file.path)) {
        newSelected.add(file.path);
      }
    });
    setSelectedFiles(newSelected);
    setDeleteResult(null);
  };

  // 处理单个删除
  const handleDeleteFile = async (filePath: string) => {
    if (!confirm('确定要删除这个文件吗？')) {
      return;
    }

    try {
      await deleteFile(filePath);
      setFiles(prevFiles => prevFiles.filter(f => f.path !== filePath));
      setSelectedFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(filePath);
        return newSet;
      });
    } catch (error: any) {
      console.error('Failed to delete file:', error);
      alert('删除失败：' + error.message);
    }
  };

  // 处理批量删除
  const handleBatchDelete = async () => {
    if (selectedFiles.size === 0) {
      return;
    }

    const count = selectedFiles.size;
    if (!confirm(`确定要删除选中的 ${count} 个文件吗？`)) {
      return;
    }

    setIsDeleting(true);
    try {
      const deletedPaths: string[] = [];
      const errors: string[] = [];

      for (const filePath of selectedFiles) {
        try {
          await deleteFile(filePath);
          deletedPaths.push(filePath);
        } catch (error: any) {
          console.error(`Failed to delete ${filePath}:`, error);
          errors.push(`${filePath}: ${error.message}`);
        }
      }

      // 更新文件列表
      setFiles(prevFiles => prevFiles.filter(f => !deletedPaths.includes(f.path)));
      
      // 清除已删除文件的选择状态
      setSelectedFiles(prev => {
        const newSet = new Set(prev);
        deletedPaths.forEach(path => newSet.delete(path));
        return newSet;
      });

      setDeleteResult({
        success: deletedPaths.length,
        failed: errors.length,
        errors: errors
      });
    } catch (error: any) {
      console.error('Batch delete error:', error);
      alert('批量删除失败：' + error.message);
    } finally {
      setIsDeleting(false);
    }
  };

  // 获取文件图标
  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    switch (ext) {
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
      case 'webp':
        return '🖼️';
      case 'pdf':
        return '📄';
      case 'doc':
      case 'docx':
        return '📝';
      case 'ppt':
      case 'pptx':
        return '📊';
      case 'txt':
      case 'md':
        return '📋';
      case 'json':
      case 'xml':
        return '📑';
      case 'py':
      case 'js':
      case 'ts':
        return '💻';
      case 'mp3':
      case 'wav':
        return '🔊';
      case 'mp4':
      case 'avi':
      case 'mov':
        return '🎬';
      default:
        return '📁';
    }
  };

  // 渲染删除结果
  const renderDeleteResult = () => {
    if (!deleteResult) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="cyber-card p-4 bg-cyber-dark/50 border-l-4 border-green-500"
      >
        <div className="flex items-center gap-3 mb-2">
          <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="font-semibold">删除完成</span>
          <span className="text-gray-400">成功 {deleteResult.success} 个，失败 {deleteResult.failed} 个</span>
        </div>
        
        {deleteResult.errors.length > 0 && (
          <details className="group mt-2">
            <summary className="cursor-pointer text-sm text-red-400 hover:text-red-300">
              查看错误详情
            </summary>
            <ul className="mt-2 space-y-1 text-sm text-red-400">
              {deleteResult.errors.map((error, index) => (
                <li key={index} className="font-mono">{error}</li>
              ))}
            </ul>
          </details>
        )}
        
        <div className="flex gap-3 pt-4 border-t border-cyber-blue/20">
          <button
            onClick={() => setDeleteResult(null)}
            className="cyber-button px-4 py-2 text-sm bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/30 hover:bg-cyber-blue/30"
          >
            关闭
          </button>
          <Link
            href="/dashboard/tasks"
            className="cyber-button px-4 py-2 text-sm bg-cyber-purple/20 text-cyber-purple border border-cyber-purple/30 hover:bg-cyber-purple/30"
          >
            查看任务
          </Link>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="space-y-6">
      {/* 标题栏 */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="text-3xl font-bold text-white">输出文件</h1>
        
        <div className="flex gap-3">
          {selectedFiles.size > 0 && (
            <>
              <button
                onClick={handleBatchDelete}
                disabled={isDeleting}
                className="cyber-button px-4 py-2 bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 disabled:opacity-50"
              >
                {isDeleting ? '删除中...' : `删除选中 (${selectedFiles.size})`}
              </button>
              <button
                onClick={handleInvertSelection}
                className="cyber-button px-4 py-2 bg-cyber-orange/20 text-cyber-orange border border-cyber-orange/30 hover:bg-cyber-orange/30"
              >
                反选
              </button>
            </>
          )}
          
          <Link
            href="/dashboard/tasks"
            className="cyber-button px-4 py-2 bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/30 hover:bg-cyber-blue/30"
          >
            返回任务列表
          </Link>
        </div>
      </div>

      {/* 操作提示 */}
      {selectedFiles.size > 0 && selectedFiles.size < files.length && (
        <div className="cyber-card p-3 bg-cyber-dark/50 border-t border-cyber-blue/10 text-center">
          <button
            onClick={handleSelectAll}
            className="text-sm text-cyber-blue hover:text-cyber-blue/80 transition-colors"
          >
            全选本页 {files.length} 个文件
          </button>
        </div>
      )}

      {/* 删除结果 */}
      {renderDeleteResult()}

      {/* 错误信息 */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="cyber-card p-4 bg-red-500/10 border-l-4 border-red-500"
        >
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-red-400">{error}</span>
          </div>
        </motion.div>
      )}

      {/* 文件列表 */}
      {loading ? (
        <div className="cyber-card text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-cyber-blue"></div>
          <p className="mt-4 text-gray-400">加载中...</p>
        </div>
      ) : files.length === 0 ? (
        <div className="cyber-card text-center py-12">
          <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <p className="text-gray-400 mb-4">暂无输出文件</p>
          <Link
            href="/dashboard/tasks/new"
            className="cyber-button px-6 py-3 bg-gradient-to-r from-cyber-blue to-cyber-purple text-white font-semibold"
          >
            创建新任务
          </Link>
        </div>
      ) : (
        <>
          {/* 统计信息 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="cyber-card p-4">
              <div className="text-2xl font-bold text-cyber-blue">{files.length}</div>
              <div className="text-sm text-gray-400">总文件数</div>
            </div>
            <div className="cyber-card p-4">
              <div className="text-2xl font-bold text-cyber-purple">{tasks.length}</div>
              <div className="text-sm text-gray-400">完成任务</div>
            </div>
            <div className="cyber-card p-4">
              <div className="text-2xl font-bold text-cyber-green">{selectedFiles.size}</div>
              <div className="text-sm text-gray-400">已选中</div>
            </div>
            <div className="cyber-card p-4">
              <div className="text-2xl font-bold text-cyber-orange">
                {(files.reduce((sum, f) => sum + (f.size || 0), 0) / 1024).toFixed(1)} KB
              </div>
              <div className="text-sm text-gray-400">总大小</div>
            </div>
          </div>

          {/* 文件网格 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {files.map((file, index) => {
              // 查找对应的任务信息
              const task = tasks.find(t => t.output_files?.includes(file.path));
              
              return (
                <motion.div
                  key={`${file.path}-${index}`}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className={`cyber-card p-6 ${
                    selectedFiles.has(file.path) ? 'ring-2 ring-cyber-blue' : ''
                  }`}
                >
                  <div className="flex items-start gap-3 mb-4">
                    <input
                      type="checkbox"
                      checked={selectedFiles.has(file.path)}
                      onChange={() => handleSelectFile(file.path)}
                      className="w-4 h-4 rounded border-cyber-blue bg-cyber-dark text-cyber-blue focus:ring-cyber-blue mt-1"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-2xl">{getFileIcon(file.name)}</span>
                        <h3 className="font-semibold text-white truncate" title={file.name}>
                          {file.name}
                        </h3>
                      </div>
                      <p className="text-xs text-gray-500 break-all">{file.path}</p>
                    </div>
                  </div>
                  
                  {/* 文件信息 */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5a2 2 0 012 2v14a2 2 0 01-2 2z" />
                      </svg>
                      <span>{(file.size / 1024).toFixed(2)} KB</span>
                    </div>
                    {task && (
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        <span className="truncate" title={task.name}>{task.name}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>{new Date(file.modified * 1000).toLocaleString('zh-CN')}</span>
                    </div>
                  </div>
                  
                  {/* 操作按钮 */}
                  <div className="flex gap-2 pt-3 border-t border-cyber-blue/10">
                    <button
                      onClick={() => downloadFile(file.path)}
                      className="flex-1 cyber-button px-3 py-2 text-sm bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/30 hover:bg-cyber-blue/30"
                    >
                      下载
                    </button>
                    <button
                      onClick={() => handleDeleteFile(file.path)}
                      className="flex-1 cyber-button px-3 py-2 text-sm bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30"
                    >
                      删除
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* 底部全选提示 */}
          {selectedFiles.size > 0 && selectedFiles.size < files.length && (
            <div className="cyber-card p-3 bg-cyber-dark/50 border-t border-cyber-blue/10 text-center">
              <button
                onClick={handleSelectAll}
                className="text-sm text-cyber-blue hover:text-cyber-blue/80 transition-colors"
              >
                全选本页 {files.length} 个文件
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
