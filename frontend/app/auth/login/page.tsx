'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { login } from '@/lib/api/auth';
import { useAuthStore } from '@/lib/store/auth';

export default function LoginPage() {
  const router = useRouter();
  const setUser = useAuthStore((state) => state.setUser);
  const setLoading = useAuthStore((state) => state.setLoading);
  const setError = useAuthStore((state) => state.setError);

  const [formData, setFormData] = useState({
    username: typeof window !== 'undefined' ? localStorage.getItem('login_username') || '' : '',
    password: ''
  });
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setErrorState] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorState('');

    try {
      setLoading(true);
      const response = await login(formData);

      // 保存用户名（如果用户选择记住我）
      if (rememberMe) {
        localStorage.setItem('login_username', formData.username);
      } else {
        localStorage.removeItem('login_username');
      }

      // 更新认证状态
      setUser(response.user);

      // 跳转到dashboard
      router.push('/dashboard');
    } catch (error: any) {
      setErrorState(error.message || '登录失败');
    } finally {
      setIsLoading(false);
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      {/* 背景效果 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyber-purple/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-cyber-blue/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-lg flex items-center justify-center">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 2L2 7l10 5 10-5-10 5M2 17l10 5 10-5M12 22V2"
                />
              </svg>
            </div>
            <span className="text-2xl font-bold text-gradient">DeepTrace</span>
          </Link>
        </div>

        {/* 登录卡片 */}
        <div className="cyber-card">
          <h1 className="text-2xl font-bold mb-6 text-center">登录</h1>

          {/* 错误提示 */}
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mb-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm"
            >
              {error}
            </motion.div>
          )}

          {/* 登录表单 */}
          <form onSubmit={handleSubmit} className="space-y-4" autoComplete="off">
            <div>
              <label htmlFor="username" className="block text-sm font-medium mb-2 text-gray-300">
                用户名
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={formData.username}
                onChange={handleInputChange}
                disabled={isLoading}
                className="cyber-input w-full"
                placeholder="请输入用户名"
                autoComplete="off"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-2 text-gray-300">
                密码
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleInputChange}
                disabled={isLoading}
                className="cyber-input w-full"
                placeholder="请输入密码"
                autoComplete="new-password"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm text-gray-400">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-gray-600 bg-gray-800 text-cyber-blue focus:ring-cyber-blue"
                />
                记住用户名
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="cyber-button w-full font-semibold py-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-cyber-blue border-t-transparent rounded-full animate-spin" />
                  <span>登录中...</span>
                </div>
              ) : (
                '登录'
              )}
            </button>
          </form>

          {/* 注册链接 */}
          <p className="mt-6 text-center text-sm text-gray-400">
            还没有账户？{' '}
            <Link href="/auth/register" className="text-cyber-blue hover:text-cyber-purple transition-colors">
              立即注册
            </Link>
          </p>
        </div>

        {/* 说明文字 */}
        <p className="text-center text-sm text-gray-500 mt-6">
          使用您的账户登录 DeepTrace，开始生成敏感数据泄露场景
        </p>
      </motion.div>
    </div>
  );
}
