'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { register } from '@/lib/api/auth';
import { useAuthStore } from '@/lib/store/auth';

export default function RegisterPage() {
  const router = useRouter();
  const setUser = useAuthStore((state) => state.setUser);
  const setLoading = useAuthStore((state) => state.setLoading);
  const setError = useAuthStore((state) => state.setError);

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setErrorState] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorState('');

    // 验证密码
    if (formData.password !== formData.confirmPassword) {
      setErrorState('两次输入的密码不一致');
      setIsLoading(false);
      return;
    }

    // 验证密码强度
    if (formData.password.length < 8) {
      setErrorState('密码长度至少为8位');
      setIsLoading(false);
      return;
    }

    try {
      setLoading(true);
      const user = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password
      });

      setSuccess(true);

      // 3秒后跳转到登录页面
      setTimeout(() => {
        router.push('/auth/login');
      }, 2000);
    } catch (error: any) {
      setErrorState(error.message || '注册失败');
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

  // 成功提示组件
  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="cyber-card text-center max-w-md"
        >
          <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold mb-2">注册成功！</h2>
          <p className="text-gray-400 mb-6">
            您的账户已创建成功，正在跳转到登录页面...
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8">
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
            <img
              src="/logo.png"
              alt="ShadowForge"
              className="w-12 h-12 rounded-lg object-cover"
            />
            <span className="text-2xl font-bold text-gradient">DeepTrace</span>
          </Link>
        </div>

        {/* 注册卡片 */}
        <div className="cyber-card">
          <h1 className="text-2xl font-bold mb-6 text-center">注册账户</h1>

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

          {/* 注册表单 */}
          <form onSubmit={handleSubmit} className="space-y-4">
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
                minLength={3}
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2 text-gray-300">
                邮箱
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                disabled={isLoading}
                className="cyber-input w-full"
                placeholder="请输入邮箱地址"
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
                placeholder="请输入密码（至少8位）"
                minLength={8}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium mb-2 text-gray-300">
                确认密码
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword}
                onChange={handleInputChange}
                disabled={isLoading}
                className="cyber-input w-full"
                placeholder="请再次输入密码"
                minLength={8}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="cyber-button w-full font-semibold py-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-cyber-blue border-t-transparent rounded-full animate-spin" />
                  <span>注册中...</span>
                </div>
              ) : (
                '注册'
              )}
            </button>
          </form>

          {/* 登录链接 */}
          <p className="mt-6 text-center text-sm text-gray-400">
            已有账户？{' '}
            <Link href="/auth/login" className="text-cyber-blue hover:text-cyber-purple transition-colors">
              立即登录
            </Link>
          </p>
        </div>

        {/* 说明文字 */}
        <p className="text-center text-sm text-gray-500 mt-6">
          注册即表示您同意我们的{' '}
          <Link href="/terms" className="text-cyber-blue hover:text-cyber-purple transition-colors">
            服务条款
          </Link>
          {' '}和{' '}
          <Link href="/privacy" className="text-cyber-blue hover:text-cyber-purple transition-colors">
            隐私政策
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
