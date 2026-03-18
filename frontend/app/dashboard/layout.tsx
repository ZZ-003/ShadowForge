'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';
import { getCurrentUser, logout } from '@/lib/api/auth';
import { motion } from 'framer-motion';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const isDemoMode = pathname === '/dashboard/demo';

  // 检查认证状态
  useEffect(() => {
    // 定义不需要认证即可访问的页面
    const publicPages = ['/dashboard/demo', '/dashboard'];
    
    // 如果当前页面不是公开页面且用户未认证，重定向到登录页面
    if (!isAuthenticated && !publicPages.includes(pathname)) {
      // 清除可能残留的用户信息
      useAuthStore.getState().clearUser();
      window.location.href = '/auth/login';
    }
  }, [isAuthenticated, pathname]);

  // 在演示模式下，清除用户信息
  useEffect(() => {
    if (isDemoMode) {
      useAuthStore.getState().clearUser();
    }
  }, [isDemoMode]);

  const handleLogout = async () => {
    try {
      await logout();
      // 重定向到首页
      window.location.href = '/';
    } catch (error) {
      console.error('Logout error:', error);
      // 即使API调用失败，也要清除本地状态并重定向
      window.location.href = '/';
    }
  };

  const menuItems = [
    { name: '概览', path: '/dashboard', icon: '📊' },
    { name: '生成任务', path: '/dashboard/tasks', icon: '⚡' },
    { name: '输出文件', path: '/dashboard/outputs', icon: '📁' },
    { name: '系统设置', path: '/dashboard/settings', icon: '⚙️' },
  ];

  return (
    <div className="flex h-screen bg-cyber-black">
      {/* 侧边栏 */}
      <motion.aside
        initial={{ width: 0 }}
        animate={{ width: sidebarOpen ? 280 : 80 }}
        transition={{ duration: 0.3 }}
        className="bg-cyber-dark border-r border-cyber-blue/20 flex flex-col overflow-hidden"
      >
        {/* Logo */}
        <div className="p-4 border-b border-cyber-blue/20">
          <Link href="/dashboard" className="flex items-center gap-3">
            <img
              src="/logo.png"
              alt="ShadowForge"
              className="w-10 h-10 rounded-lg object-cover flex-shrink-0"
            />
            {sidebarOpen && (
              <span className="text-xl font-bold text-gradient">DeepTrace</span>
            )}
          </Link>
        </div>

        {/* 菜单 */}
        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => {
            const isActive = pathname === item.path;
            return (
              isDemoMode ? (
                <div
                  key={item.path}
                  onClick={() => {
                    window.location.href = '/auth/login';
                  }}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 cursor-pointer ${
                    'text-gray-400'
                  }`}
                >
                  <span className="text-xl flex-shrink-0">{item.icon}</span>
                  {sidebarOpen && <span className="font-medium">{item.name}</span>}
                </div>
              ) : (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/30'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-cyber-blue/10'
                  }`}
                >
                  <span className="text-xl flex-shrink-0">{item.icon}</span>
                  {sidebarOpen && <span className="font-medium">{item.name}</span>}
                </Link>
              )
            );
          })}
        </nav>

        {/* 用户信息 */}
        <div className="p-4 border-t border-cyber-blue/20">
          {isDemoMode ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-gray-500 to-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold">G</span>
              </div>
              {sidebarOpen && (
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">游客登录</p>
                  <p className="text-xs text-gray-500 truncate"></p>
                </div>
              )}
            </div>
          ) : isAuthenticated && user ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold">
                  {user.username.charAt(0).toUpperCase()}
                </span>
              </div>
              {sidebarOpen && (
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{user.username}</p>
                  <p className="text-xs text-gray-500 truncate">{user.email}</p>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg hover:bg-cyber-blue/10 transition-colors flex-shrink-0"
                title="退出登录"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4 4m4-4h3a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
          ) : (
            <Link href="/auth/login" className="cyber-button w-full text-sm">
              登录
            </Link>
          )}
        </div>
      </motion.aside>

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* 顶部导航 */}
        <header className="bg-cyber-dark border-b border-cyber-blue/20 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* 侧边栏切换按钮 */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-cyber-blue/10 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            {/* 面包屑 */}
            <nav className="text-sm text-gray-400">
              <span>DeepTrace</span>
              <span className="mx-2">/</span>
              <span className="text-gray-200">Dashboard</span>
            </nav>
          </div>

          {/* 右侧操作 - 已移除通知和设置图标 */}
        </header>

        {/* 主内容 */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
