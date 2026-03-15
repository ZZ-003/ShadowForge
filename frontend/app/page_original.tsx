'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* 英雄区域 */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* 动态背景 */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyber-purple/20 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-cyber-blue/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
        </div>

        {/* 主内容 */}
        <div className="relative z-10 text-center px-4">
          {/* Logo区域 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-8"
          >
            <div className="inline-flex items-center gap-3">
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
              <h1 className="text-4xl md:text-5xl font-bold text-gradient">
                DeepTrace
              </h1>
            </div>
          </motion.div>

          {/* 标题 */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="text-xl md:text-2xl text-gray-400 mb-6 font-light"
          >
            多模态敏感数据深度仿真引擎
          </motion.p>

          {/* 描述 */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            生成包含敏感信息的多模态泄露场景，用于安全测试、数据集构建和演示。
            支持 IDE、CLI、聊天、配置文件等多种场景，输出图片、视频、音频、PDF、Word、PPT 等多种格式。
          </motion.p>

          {/* CTA按钮 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link
              href="/dashboard"
              className="cyber-button px-8 py-4 text-lg font-semibold inline-flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a4 4 0 002 1v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a4 4 0 002-1v1a3 3 0 01-3 3H6z" />
              </svg>
              进入 Dashboard
            </Link>

            <Link
              href="/auth/register"
              className="px-8 py-4 text-lg font-semibold border border-cyber-blue/30 rounded-lg hover:bg-cyber-blue/10 transition-all duration-300"
            >
              注册账户
            </Link>
          </motion.div>
        </div>

        {/* 滚动提示 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.8 }}
          className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
        >
          <svg className="w-6 h-6 text-gray-600 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </motion.div>
      </section>

      {/* 特性展示 */}
      <section className="py-24 px-4 relative">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gradient">
              核心功能
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              强大的多模态生成能力，满足各种安全测试场景需求
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                className="cyber-card group"
              >
                <div className="text-cyber-blue mb-4">
                  <feature.icon />
                </div>
                <h3 className="text-xl font-semibold mb-2 group-hover:text-cyber-blue transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-400 text-sm">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* 支持的模态 */}
      <section className="py-24 px-4 relative bg-cyber-dark/50">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gradient">
              支持的模态
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              多种输出格式，满足不同场景需求
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {modalities.map((modality, index) => (
              <motion.div
                key={modality.name}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.05, duration: 0.4 }}
                className="cyber-card text-center group cursor-pointer hover:scale-105 transition-transform"
              >
                <div className="text-3xl mb-2">
                  {modality.icon}
                </div>
                <h3 className="font-semibold text-sm group-hover:text-cyber-blue transition-colors">
                  {modality.name}
                </h3>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* 技术栈 */}
      <section className="py-24 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gradient">
              技术栈
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              基于现代化技术栈构建
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {techStack.map((tech, index) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                className="cyber-card text-center"
              >
                <div className="text-4xl mb-3">
                  {tech.icon}
                </div>
                <h3 className="font-semibold mb-1">
                  {tech.name}
                </h3>
                <p className="text-sm text-gray-400">
                  {tech.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA区域 */}
      <section className="py-24 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyber-purple/10 to-cyber-blue/10" />
        <div className="container mx-auto max-w-4xl relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="cyber-card text-center"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-gradient">
              开始使用 DeepTrace
            </h2>
            <p className="text-gray-400 mb-8 max-w-xl mx-auto">
              注册账户，立即开始生成您的第一个敏感数据泄露场景
            </p>
            <Link
              href="/auth/register"
              className="cyber-button px-10 py-4 text-lg font-semibold inline-flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8-8V5a4 4 0 014-8v8zm-2 5a6 6 0 010 12v3a2 2 0 01-2 2H6a2 2 0 01-2-2v-3a6 6 0 010-12z" />
              </svg>
              立即注册
            </Link>
          </motion.div>
        </div>
      </section>

      {/* 页脚 */}
      <footer className="py-8 px-4 border-t border-cyber-blue/20">
        <div className="container mx-auto max-w-6xl">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-500">
              © 2024 DeepTrace. All rights reserved.
            </p>
            <div className="flex gap-6">
              <Link href="/docs" className="text-sm text-gray-500 hover:text-cyber-blue transition-colors">
                文档
              </Link>
              <Link href="/privacy" className="text-sm text-gray-500 hover:text-cyber-blue transition-colors">
                隐私政策
              </Link>
              <Link href="/terms" className="text-sm text-gray-500 hover:text-cyber-blue transition-colors">
                服务条款
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}

// 特性数据
const features = [
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4 4M4 4h16" />
      </svg>
    ),
    title: '智能场景生成',
    description: '基于 LLM 智能分析敏感类型，自动选择最真实的泄露场景'
  },
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    title: '多格式输出',
    description: '支持图片、视频、音频、PDF、Word、PPT 等多种输出格式'
  },
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0m-9 2h9m-9-8h9m-9 4h9m-9-4h9m5 4h-3m-3-4h3" />
      </svg>
    ),
    title: '高质量渲染',
    description: '专业级渲染引擎，生成逼真的界面和文档效果'
  },
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    ),
    title: '批量处理',
    description: '支持批量任务创建，提高工作效率'
  },
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
      </svg>
    ),
    title: '实时监控',
    description: '任务进度实时更新，随时掌握生成状态'
  },
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 22s8-4 8-10V5l8-10v27z" />
      </svg>
    ),
    title: '安全可靠',
    description: '数据安全存储，支持用户隔离和权限控制'
  }
];

// 模态数据
const modalities = [
  {
    name: '图片',
    icon: '🖼️'
  },
  {
    name: '视频',
    icon: '🎬'
  },
  {
    name: '音频',
    icon: '🎵'
  },
  {
    name: 'PDF',
    icon: '📄'
  },
  {
    name: 'Word',
    icon: '📝'
  },
  {
    name: 'PPT',
    icon: '📊'
  }
];

// 技术栈数据
const techStack = [
  {
    name: 'Next.js 14',
    description: 'React框架',
    icon: '⚛️'
  },
  {
    name: 'FastAPI',
    description: 'Python Web框架',
    icon: '⚡'
  },
  {
    name: 'Tailwind CSS',
    description: '样式框架',
    icon: '🎨'
  },
  {
    name: 'PostgreSQL',
    description: '数据库',
    icon: '🐘'
  }
];
