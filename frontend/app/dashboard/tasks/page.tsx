'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/lib/store/auth';
import { getTasks, deleteTask, deleteTasksBatch, TaskStatus, BatchDeleteResponse } from '@/lib/api/tasks';

export default function TasksPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<TaskStatus | null>(null);
  const [selectedTasks, setSelectedTasks] = useState<Set<number>>(new Set());
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteResult, setDeleteResult] = useState<BatchDeleteResponse | null>(null);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    // 检查认证状态
    if (!isAuthenticated) {
      window.location.href = '/auth/login';
      return;
    }
    
    loadTasks();
  }, [filter, isAuthenticated]);

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      const data = await getTasks(filter ? { status: filter } : undefined);
      setTasks(data);
    } catch (error: any) {
      console.error('Failed to load tasks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 处理单个任务选择
  const handleSelectTask = (taskId: number) => {
    const newSelected = new Set(selectedTasks);
    if (newSelected.has(taskId)) {
      newSelected.delete(taskId);
    } else {
      newSelected.add(taskId);
    }
    setSelectedTasks(newSelected);
    setDeleteResult(null);
  };

  // 全选/反选
  const handleSelectAll = () => {
    if (selectedTasks.size === filteredTasks.length) {
      setSelectedTasks(new Set());
    } else {
      setSelectedTasks(new Set(filteredTasks.map(t => t.id)));
    }
    setDeleteResult(null);
  };

  // 反选
  const handleInvertSelection = () => {
    const newSelected = new Set<number>();
    filteredTasks.forEach(task => {
      if (!selectedTasks.has(task.id)) {
        newSelected.add(task.id);
      }
    });
    setSelectedTasks(newSelected);
    setDeleteResult(null);
  };

  // 处理单个删除
  const handleDelete = async (taskId: number) => {
    if (!confirm('确定要删除这个任务及其所有文件吗？')) {
      return;
    }

    try {
      await deleteTask(taskId);
      setTasks(tasks.filter(t => t.id !== taskId));
      setSelectedTasks(prev => {
        const newSet = new Set(prev);
        newSet.delete(taskId);
        return newSet;
      });
    } catch (error: any) {
      console.error('Failed to delete task:', error);
      alert('删除失败：' + error.message);
    }
  };

  // 处理批量删除
  const handleBatchDelete = async () => {
    if (selectedTasks.size === 0) {
      return;
    }

    const count = selectedTasks.size;
    if (!confirm(`确定要删除选中的 ${count} 个任务及其所有文件吗？`)) {
      return;
    }

    setIsDeleting(true);
    setDeleteResult(null);

    try {
      const response = await deleteTasksBatch(Array.from(selectedTasks));
      setDeleteResult(response);

      // 从列表中移除已删除的任务
      setTasks(prevTasks => 
        prevTasks.filter(t => !response.deleted_tasks.includes(t.id))
      );

      // 清空选择
      setSelectedTasks(new Set());
    } catch (error: any) {
      console.error('Failed to batch delete tasks:', error);
      alert('批量删除失败：' + error.message);
    } finally {
      setIsDeleting(false);
    }
  };

  // 获取筛选后的任务列表
  const filteredTasks = filter 
    ? tasks.filter(t => t.status === filter)
    : tasks;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-500 bg-yellow-500/20';
      case 'running':
        return 'text-blue-500 bg-blue-500/20';
      case 'completed':
        return 'text-green-500 bg-green-500/20';
      case 'failed':
        return 'text-red-500 bg-red-500/20';
      case 'cancelled':
        return 'text-gray-500 bg-gray-500/20';
      default:
        return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '等待中';
      case 'running':
        return '进行中';
      case 'completed':
        return '已完成';
      case 'failed':
        return '失败';
      case 'cancelled':
        return '已取消';
      default:
        return status;
    }
  };

  // 渲染批量删除结果
  const renderDeleteResult = () => {
    if (!deleteResult) return null;

    const successCount = deleteResult.success_count;
    const failedCount = deleteResult.failed_count;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="cyber-card space-y-4"
      >
        <h2 className="text-lg font-semibold text-cyber-blue">批量删除结果</h2>
        
        {/* 统计信息 */}
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
            <div className="text-2xl font-bold text-green-400">{successCount}</div>
            <div className="text-sm text-gray-400">成功删除</div>
          </div>
          <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
            <div className="text-2xl font-bold text-red-400">{failedCount}</div>
            <div className="text-sm text-gray-400">失败</div>
          </div>
          <div className="p-4 bg-cyber-blue/20 border border-cyber-blue/30 rounded-lg">
            <div className="text-2xl font-bold text-cyber-blue">{successCount + failedCount}</div>
            <div className="text-sm text-gray-400">总计</div>
          </div>
        </div>

        {/* 失败详情 */}
        {failedCount > 0 && (
          <div className="space-y-2">
            <h3 className="font-medium text-red-400">失败详情：</h3>
            {deleteResult.errors.map((error, index) => (
              <div key={index} className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm">
                <span className="text-red-400">错误:</span> {error}
              </div>
            ))}
          </div>
        )}

        {/* 操作按钮 */}
        <div className="flex gap-3 pt-4">
          <button
            onClick={() => {
              setDeleteResult(null);
              loadTasks();
            }}
            className="cyber-button px-6 py-2 inline-flex items-center gap-2 bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/30"
          >
            刷新列表
          </button>
          <Link
            href="/dashboard/tasks/new"
            className="cyber-button px-6 py-2 inline-flex items-center gap-2 bg-cyber-dark text-gray-300 border border-cyber-blue/20 hover:bg-cyber-blue/10"
          >
            创建新任务
          </Link>
        </div>
      </motion.div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyber-blue border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 标题和操作 */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h1 className="text-3xl font-bold">生成任务</h1>
        <Link
          href="/dashboard/tasks/new"
          className="cyber-button px-6 py-3 inline-flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          创建新任务
        </Link>
      </div>

      {/* 批量删除结果 */}
      {deleteResult && renderDeleteResult()}

      {/* 筛选器 */}
      <div className="cyber-card">
        <div className="flex flex-wrap gap-2">
          {Object.values(TaskStatus).map((status) => (
            <button
              key={status}
              onClick={() => setFilter(filter === status ? null : status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === status
                  ? 'bg-cyber-blue text-cyber-black'
                  : 'bg-cyber-dark text-gray-400 hover:text-gray-200'
              }`}
            >
              {getStatusText(status)}
            </button>
          ))}
        </div>
      </div>

      {/* 任务列表 */}
      {filteredTasks.length > 0 ? (
        <div className="cyber-card overflow-hidden">
          {/* 顶部工具栏 - 显示选中数量和批量操作按钮 */}
          {selectedTasks.size > 0 && (
            <div className="p-4 bg-cyber-blue/10 border-b border-cyber-blue/20 flex flex-wrap gap-4 items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-cyber-blue font-medium">
                  已选择 {selectedTasks.size} 个任务
                </span>
                <button
                  onClick={handleInvertSelection}
                  className="text-sm text-gray-400 hover:text-cyber-blue transition-colors"
                >
                  反选
                </button>
              </div>
              <button
                onClick={handleBatchDelete}
                disabled={isDeleting}
                className="px-4 py-2 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isDeleting ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    删除中...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    批量删除
                  </>
                )}
              </button>
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-cyber-blue/20">
                  <th className="text-center p-4 w-12">
                    <input
                      type="checkbox"
                      checked={filteredTasks.length > 0 && selectedTasks.size === filteredTasks.length}
                      onChange={handleSelectAll}
                      className="w-4 h-4 rounded border-cyber-blue bg-cyber-dark text-cyber-blue focus:ring-cyber-blue"
                    />
                  </th>
                  <th className="text-left p-4 font-semibold text-gray-300">名称</th>
                  <th className="text-left p-4 font-semibold text-gray-300">类型</th>
                  <th className="text-left p-4 font-semibold text-gray-300">模态</th>
                  <th className="text-left p-4 font-semibold text-gray-300">状态</th>
                  <th className="text-left p-4 font-semibold text-gray-300">进度</th>
                  <th className="text-left p-4 font-semibold text-gray-300">创建时间</th>
                  <th className="text-right p-4 font-semibold text-gray-300">操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredTasks.map((task, index) => (
                  <motion.tr
                    key={task.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05, duration: 0.3 }}
                    className={`border-b border-cyber-blue/10 hover:bg-cyber-blue/5 transition-colors ${
                      selectedTasks.has(task.id) ? 'bg-cyber-blue/10' : ''
                    }`}
                  >
                    <td className="p-4 text-center">
                      <input
                        type="checkbox"
                        checked={selectedTasks.has(task.id)}
                        onChange={() => handleSelectTask(task.id)}
                        className="w-4 h-4 rounded border-cyber-blue bg-cyber-dark text-cyber-blue focus:ring-cyber-blue"
                      />
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <Link
                          href={`/dashboard/tasks/${task.id}`}
                          className="font-medium hover:text-cyber-blue transition-colors"
                        >
                          {task.name}
                        </Link>
                        {task.description && (
                          <p className="text-xs text-gray-500 truncate max-w-md">
                            {task.description}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="cyber-badge">{task.secret_type}</span>
                    </td>
                    <td className="p-4">
                      <span className={`text-sm font-mono ${task.modality === 'video' ? 'text-cyber-purple' : 'text-cyber-blue'}`}>
                        {task.modality.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                        {getStatusText(task.status)}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 w-32 h-2 bg-cyber-dark rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-cyber-blue to-cyber-purple transition-all duration-300"
                            style={{ width: `${task.progress}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-400 w-12 text-right">{task.progress}%</span>
                      </div>
                    </td>
                    <td className="p-4 text-sm text-gray-400">
                      {new Date(task.created_at).toLocaleString('zh-CN')}
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleDelete(task.id)}
                          className="p-2 rounded-lg hover:bg-red-500/10 text-gray-400 hover:text-red-500 transition-colors"
                          title="删除任务"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 底部全选提示 */}
          {selectedTasks.size > 0 && selectedTasks.size < filteredTasks.length && (
            <div className="p-3 bg-cyber-dark/50 border-t border-cyber-blue/10 text-center">
              <button
                onClick={handleSelectAll}
                className="text-sm text-cyber-blue hover:text-cyber-blue/80 transition-colors"
              >
                全选本页 {filteredTasks.length} 个任务
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="cyber-card text-center py-12">
          <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5a2 2 0 012 2v14a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-xl font-semibold mb-2">暂无任务</h3>
          <p className="text-gray-400 mb-6">
            {filter ? '没有找到符合条件的任务' : '您还没有创建任何任务'}
          </p>
          <Link
            href="/dashboard/tasks/new"
            className="cyber-button px-6 py-3 inline-flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            创建新任务
          </Link>
        </div>
      )}
    </div>
  );
}
