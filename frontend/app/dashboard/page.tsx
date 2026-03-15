'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/lib/store/auth';
import Link from 'next/link';
import { getTasks } from '@/lib/api/tasks';

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [stats, setStats] = useState({
    totalTasks: 0,
    completedTasks: 0,
    pendingTasks: 0,
    failedTasks: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/auth/login';
      return;
    }
  }, [isAuthenticated]);

  useEffect(() => {
    // 只有在用户认证时才加载统计数据
    if (user) {
      loadStats();
    } else {
      setIsLoading(false);
    }
  }, [user]);

  const loadStats = async () => {
    try {
      setIsLoading(true);
      const tasks = await getTasks();

      setStats({
        totalTasks: tasks.length,
        completedTasks: tasks.filter(t => t.status === 'completed').length,
        pendingTasks: tasks.filter(t => t.status === 'pending').length,
        failedTasks: tasks.filter(t => t.status === 'failed').length,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const statCards = [
    {
      name: '总任务数',
      value: stats.totalTasks,
      icon: '📊',
      color: 'from-cyber-blue to-cyber-purple',
    },
    {
      name: '已完成',
      value: stats.completedTasks,
      icon: '✅',
      color: 'from-cyber-green to-emerald-500',
    },
    {
      name: '进行中',
      value: stats.pendingTasks,
      icon: '⏳',
      color: 'from-cyber-yellow to-amber-500',
    },
    {
      name: '失败',
      value: stats.failedTasks,
      icon: '❌',
      color: 'from-cyber-red to-rose-500',
    },
  ];

  const recentActivities = [
    { type: 'success', message: '任务 "API Key泄露场景" 已完成', time: '2分钟前' },
    { type: 'info', message: '创建了新任务 "数据库URL泄露"', time: '5分钟前' },
    { type: 'success', message: '任务 "JWT Secret场景" 已完成', time: '10分钟前' },
  ];

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
      {/* 欢迎信息 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="cyber-card"
      >
        <h1 className="text-3xl font-bold mb-2">
          {user ? `欢迎回来，${user.username}！` : '欢迎使用 DeepTrace！'}
        </h1>
        <p className="text-gray-400">
          今天是开始新任务的绝佳时机
        </p>
      </motion.div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.4 }}
            className="cyber-card group"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-gray-400 mb-1">{stat.name}</p>
                <p className="text-3xl font-bold">{stat.value}</p>
              </div>
              <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-lg flex items-center justify-center`}>
                <span className="text-2xl">{stat.icon}</span>
              </div>
            </div>
            <div className="h-1 bg-gradient-to-r from-cyber-blue to-cyber-purple opacity-20 group-hover:opacity-40 transition-opacity" />
          </motion.div>
        ))}
      </div>

      {/* 快速操作 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        <h2 className="text-xl font-semibold mb-4">快速操作</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/dashboard/tasks/new"
            className="cyber-card group p-6 hover:scale-105 transition-transform"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-lg flex items-center justify-center">
                <span className="text-2xl">⚡</span>
              </div>
              <div>
                <h3 className="font-semibold group-hover:text-cyber-blue transition-colors">
                  创建新任务
                </h3>
                <p className="text-sm text-gray-400">
                  开始生成新的敏感数据泄露场景
                </p>
              </div>
            </div>
          </Link>

          <Link
            href="/dashboard/tasks"
            className="cyber-card group p-6 hover:scale-105 transition-transform"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-cyber-green to-emerald-500 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📋</span>
              </div>
              <div>
                <h3 className="font-semibold group-hover:text-cyber-green transition-colors">
                  查看所有任务
                </h3>
                <p className="text-sm text-gray-400">
                  管理您的生成任务
                </p>
              </div>
            </div>
          </Link>
        </div>
      </motion.div>

      {/* 最近活动 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.6 }}
        className="cyber-card"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">最近活动</h2>
          <Link href="/dashboard/tasks" className="text-sm text-cyber-blue hover:text-cyber-purple transition-colors">
            查看全部 →
          </Link>
        </div>

        <div className="space-y-3">
          {recentActivities.length > 0 ? (
            recentActivities.map((activity, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05, duration: 0.3 }}
                className="flex items-start gap-3 p-3 bg-cyber-dark/50 rounded-lg"
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  activity.type === 'success'
                    ? 'bg-green-500/20 text-green-500'
                    : activity.type === 'error'
                    ? 'bg-red-500/20 text-red-500'
                    : 'bg-cyber-blue/20 text-cyber-blue'
                }`}>
                  {activity.type === 'success' ? (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm">{activity.message}</p>
                  <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-400">暂无最近活动</p>
            </div>
          )}
        </div>
      </motion.div>

      {/* 帮助提示 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.6 }}
        className="cyber-card bg-gradient-to-r from-cyber-blue/10 to-cyber-purple/10"
      >
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-lg flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332-.477 4.5-1.253V6.253z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 6.253v13M8.5 6.253v13M8.5 6.253v13c0 .966.784 1.75 1.75 1.75h4.5c.966 0 1.75-.784 1.75-1.75V6.253c0-.966-.784-1.75-1.75-1.75H8.5z" />
            </svg>
          </div>
          <div>
            <h3 className="font-semibold mb-2">需要帮助？</h3>
            <p className="text-sm text-gray-400 mb-3">
              查看我们的文档了解如何使用 DeepTrace 生成高质量的敏感数据泄露场景
            </p>
            <Link
              href="/docs"
              className="cyber-button px-6 py-2 text-sm inline-flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5a2 2 0 012 2v14a2 2 0 01-2 2z" />
              </svg>
              查看文档
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
